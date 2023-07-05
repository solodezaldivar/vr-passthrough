import json
import os
import pickle
import socket
import struct
import sys
import wget
import torch
import time
import torchaudio
import numpy as np
import io
from torch.cuda.amp import autocast
sys.path.append('C:/Users/Master Projekt/Documents/GitHub/vr-passthrough')
print(sys.path)
from MP_sound_ml_pipeline.ast_package.src.models import ASTModel
from MP_sound_ml_pipeline.audio_preprocess import AudioPreprocessor
import csv
import pandas as pd
import noisereduce

import pyaudio
from dotenv import load_dotenv

load_dotenv()


# HOST = os.environ.get('IP')
# PORT = os.environ.get('AUDIO_TRANSPORT_PORT')
HOST = "192.168.137.1"
PORT = 9956
FORMAT = pyaudio.paInt16
CHANNELS = 2
CHUNK = 16000
RATE = 16000
os.environ['TORCH_HOME'] = 'MP_sound_ml_pipeline/ast_package/pretrained_models'


def getAudioDevices():
    print(audio.get_default_output_device_info())
    for i in range(audio.get_device_count()):
        dev = audio.get_device_info_by_index(i)
        print((i, dev['name'], dev['maxOutputChannels'], dev['maxInputChannels']))
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT,
                    channels=2,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)


def load_label(label_csv):
    with open(label_csv, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        lines = list(reader)
    labels = []
    ids = []  # Each label has a unique id such as "/m/068hy"
    for i1 in range(1, len(lines)):
        id = lines[i1][1]
        label = lines[i1][2]
        ids.append(id)
        labels.append(label)
    return labels


class ASTModelVis(ASTModel):

    def get_att_map(self, block, x):
        qkv = block.attn.qkv
        num_heads = block.attn.num_heads
        scale = block.attn.scale
        B, N, C = x.shape
        qkv = qkv(x).reshape(B, N, 3, num_heads, C // num_heads).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]  # make torchscript happy (cannot use tensor as tuple)
        attn = (q @ k.transpose(-2, -1)) * scale
        attn = attn.softmax(dim=-1)
        return attn

    def forward_visualization(self, x):
        # expect input x = (batch_size, time_frame_num, frequency_bins), e.g., (12, 1024, 128)
        x = x.unsqueeze(1)
        x = x.transpose(2, 3)

        B = x.shape[0]
        x = self.v.patch_embed(x)
        cls_tokens = self.v.cls_token.expand(B, -1, -1)
        dist_token = self.v.dist_token.expand(B, -1, -1)
        x = torch.cat((cls_tokens, dist_token, x), dim=1)
        x = x + self.v.pos_embed
        x = self.v.pos_drop(x)
        # save the attention map of each of 12 Transformer layer
        att_list = []
        for blk in self.v.blocks:
            cur_att = self.get_att_map(blk, x)
            att_list.append(cur_att)
            x = blk(x)
        return att_list


def make_features(data, mel_bins, target_length=1024):
    waveform = torch.Tensor(np.frombuffer(data, dtype=np.int16))
    waveform = waveform.unsqueeze(0)  # Add a batch dimension
   
    sr = 16000
    
    assert sr == 16000, 'input audio sampling rate must be 16kHz'

    fbank = torchaudio.compliance.kaldi.fbank(
        waveform, htk_compat=True, sample_frequency=sr, use_energy=False,
        window_type='hanning', num_mel_bins=mel_bins, dither=0.0, frame_shift=10)

    n_frames = fbank.shape[0]

    p = target_length - n_frames
    if p > 0:
        m = torch.nn.ZeroPad2d((0, 0, 0, p))
        fbank = m(fbank)
    elif p < 0:
        fbank = fbank[0:target_length, :]

    fbank = (fbank - (-4.2677393)) / (4.5689974 * 2)
    return fbank


def predict_audio(file_path: str):
    feats = make_features(file_path, mel_bins=128)  # shape(1024, 128)
    feats_data = feats.expand(1, input_tdim, 128)  # reshape the feature
    feats_data = feats_data.to(torch.device("cuda:0"))
    # do some masking of the input
    # feats_data[:, :512, :] = 0.

    # Make the prediction
    start = time.time()
    with torch.no_grad():
        with autocast():
            output = audio_model.forward(feats_data)
            output = torch.sigmoid(output)
    result_output = output.data.cpu().numpy()[0]
    sorted_indexes = np.argsort(result_output)[::-1]
    end = time.time()

    # Print audio tagging top probabilities
    print('Predice results:')
    for k in range(10):
        print('- {}: {:.4f}'.format(np.array(labels)[sorted_indexes[k]], result_output[sorted_indexes[k]]))

    elapsed_time = end - start

    result_dict = {'file': file_path.split('/')[-1].replace('.flac', ''), 'elapsed_time': elapsed_time}

    for k in range(3):
        result_dict['label' + str(k + 1)] = np.array(labels)[sorted_indexes[k]]
        result_dict['score' + str(k + 1)] = result_output[sorted_indexes[k]]

    return result_dict



def predict_audio_chunk(chunk):
    feats = make_features(chunk, mel_bins=128)  # shape(1024, 128)
    feats_data = feats.expand(1, input_tdim, 128)  # reshape the feature
    feats_data = feats_data.to(torch.device("cuda:0"))
    # do some masking of the input
    # feats_data[:, :512, :] = 0.

    # Make the prediction
    # start = time.time()
    with torch.no_grad():
        with autocast():
            output = audio_model.forward(feats_data)
            output = torch.sigmoid(output)
    result_output = output.data.cpu().numpy()[0]
    sorted_indexes = np.argsort(result_output)[::-1]
    # end = time.time()

    # Print audio tagging top probabilities
    print('Predice results:')
    # print(result_output)
    for k in range(5):
        print('- {}: {:.4f}'.format(np.array(labels)[sorted_indexes[k]], result_output[sorted_indexes[k]]))
    # print('- {}: {:.4f}'.format(np.array(labels)[sorted_indexes[0]], result_output[sorted_indexes[0]]))
    # elapsed_time = end - start

    # result_dict = {'file': file_path.split('/')[-1].replace('.flac', ''), 'elapsed_time': elapsed_time}

    # for k in range(3):
    #     result_dict['label' + str(k + 1)] = np.array(labels)[sorted_indexes[k]]
    #     result_dict['score' + str(k + 1)] = result_output[sorted_indexes[k]]

    return result_output

def apply_fade_effects(audio_data, sample_rate=16000, fade_duration=0.05):
    fade_samples = int(fade_duration * sample_rate)
    fade_in = np.linspace(0.0, 1.0, fade_samples)
    fade_out = np.linspace(1.0, 0.0, fade_samples)

    # Apply fade-in and fade-out effects to the audio data
    audio_data[:fade_samples] *= fade_in
    audio_data[-fade_samples:] *= fade_out

    return audio_data

# TODO remove clicking sound - my best guess - we need to do smth about the CHUNK size
def server():
    print("start")
    # Create an AST model and download the AudioSet pretrained weights
    # audio_preprocessor = AudioPreprocessor()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print("Listening on %s:%s..." % (HOST, str(PORT)))
    conn, addr = server_socket.accept()
    print(f'Connected to {addr}')
    data_buffer = b''
    results_list = []
    cross_fade = 100
    prev_chunk = None
    # while True:
    #     try:
    #         data = conn.recv(CHUNK)
    #         if not data:
    #             break

    #         # Convert the received data to numpy array
    #         audio_chunk = np.frombuffer(data, dtype=np.int16)

    #         # Apply fade-in effect
    #         fade_in_samples = int(0.05 * 16000)  # Number of samples for fade-in effect
    #         fade_in = np.linspace(0.0, 1.0, fade_in_samples)
    #         audio_chunk[:fade_in_samples] = np.multiply(audio_chunk[:fade_in_samples], fade_in)

    #         # Apply fade-out effect
    #         fade_out_samples = int(0.05 * 16000)  # Number of samples for fade-out effect
    #         fade_out = np.linspace(1.0, 0.0, fade_out_samples)
    #         audio_chunk[-fade_out_samples:] = np.multiply(audio_chunk[-fade_out_samples:], fade_out)

    #         # Concatenate the previous chunk and current chunk with cross-fading
    #         if prev_chunk is not None:
    #             cross_fade_samples = min(fade_out_samples, fade_in_samples)
    #             cross_chunk = np.zeros(cross_fade_samples, dtype=np.int16)
    #             for i in range(cross_fade_samples):
    #                 weight_c = float(i) / cross_fade_samples
    #                 weight_p = 1.0 - weight_c
    #                 cross_chunk[i] = int(weight_p * prev_chunk[-cross_fade_samples+i] + weight_c * audio_chunk[i])
    #             stream_data = np.concatenate((prev_chunk[:-cross_fade_samples], cross_chunk, audio_chunk[cross_fade_samples:]))
    #         else:
    #             stream_data = audio_chunk

    #         # Update the previous chunk
    #         prev_chunk = audio_chunk

    #         # Transmit the stream data over the socket
    #         stream.write(stream_data.tobytes()) 


    #     except Exception as e:
    #         print(e)
    #         pass
    buff = []
    while True:
        try:
            data = conn.recv(CHUNK)
            # Convert audio data to numpy.float64
            # results_list.append(res_dict)
            if not data:
                break
            stream.write(data)
            res_dict = predict_audio_chunk(data)

            # df = pd.DataFrame(results_list)
            # df.to_csv('first_try_results_uzh_comp.csv', index=False, header=True)
            


        except Exception as e:
            print(e)
            pass

if __name__ == '__main__':
    audioset_mdl_url = 'https://www.dropbox.com/s/cv4knew8mvbrnvq/audioset_0.4593.pth?dl=1'
    path = os.path.join("C:\\", "Users", "Master Projekt", "Documents", "Github", "vr-passthrough", "MP_sound_ml_pipeline", "ast_package", "pretrained_models", "audio_mdl.pth")
    if not os.path.exists(path):
        wget.download(audioset_mdl_url, out=path)

#     # Assume each input spectrogram has 1024 time frames
    input_tdim = 1024
    checkpoint_path = path
#     # now load the visualization model
    ast_mdl = ASTModelVis(label_dim=527, input_tdim=input_tdim, imagenet_pretrain=False,
                          audioset_pretrain=False)
    print(f'[*INFO] load checkpoint: {checkpoint_path}')
    checkpoint = torch.load(checkpoint_path, map_location='cuda')
    audio_model = torch.nn.DataParallel(ast_mdl, device_ids=[0])
    audio_model.load_state_dict(checkpoint)
    audio_model = audio_model.to(torch.device("cuda:0"))
    audio_model.eval()

#     # Load the AudioSet label set
    label_csv = os.path.join("C:\\", "Users", "Master Projekt", "Documents", "Github", "vr-passthrough", "MP_sound_ml_pipeline", "ast_package", "egs", "audioset", "data", "class_labels_indices.csv")
    labels = load_label(label_csv)

    # Get a sample audio and make feature for predict
    # change url to play with the script
    # sample_audio_path = 'https://www.dropbox.com/s/kx8s8irzwj6nbeq/glLQrEijrKg_000300.flac?dl=1'

    # # some other samples
    # sample_audio_path = 'https://www.dropbox.com/s/0ru6f8tk2x4177g/241829__lewis100011__heavy-door_16Khz.wav?dl=1'
    # sample_audio_path = 'https://www.dropbox.com/s/omned2muw8cyunf/6jiO0tPLK7U_000090.flac?dl=1'

    # if os.path.exists('ast_package/sample_audios') == False:
    #     os.mkdir('ast_package/sample_audios')
    # if os.path.exists('ast_package/sample_audios/sample_audio.flac') == True:
    #     os.remove('ast_package/sample_audios/sample_audio.flac')
    # wget.download(sample_audio_path, 'ast_package/sample_audios/sample_audio.flac')


     #results_list = []
     #for a_slice in slice_list:
    #   res_dict = predict_audio(a_slice)
     #    results_list.append(res_dict)
    #
    # df = pd.DataFrame(results_list)
    # df.to_csv('second_try_results_uzh.csv', index=False, header=True)
    #
    # results_list = []
    # for a_slice in slice_list:
    #     res_dict = predict_audio(a_slice)
    #     results_list.append(res_dict)
    #
    # df = pd.DataFrame(results_list)
    # df.to_csv('third_try_results_uzh.csv', index=False, header=True)

    server()
