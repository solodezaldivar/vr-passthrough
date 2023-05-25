import soundfile
import librosa
from pydub import AudioSegment
import os


class AudioPreprocessor:

    def __init__(self, target_formate='flac', orig_format='m4a'):
        self._target_format = target_formate
        self._orig_format = orig_format
        self._audio_raw = None
        self._conv_audio = None
        self._conv_path = None
        self._orig_path = None

    def set_orig_formate(self, orig_format):
        self._orig_format = orig_format

    def set_target_formate(self, target_format):
        self._target_format = target_format

    def set_conv_path(self, path: str):
        self._conv_path = path

    def set_orig_path(self, path: str):
        self._orig_path = path

    def set_conv_audio(self, path: str, in_format: str):
        self._conv_audio = AudioSegment.from_(path, in_format)
        self.set_orig_path(path)

    def convert_file(self, path: str):
        self._audio_raw = AudioSegment.from_file(path, self._orig_format)
        self._orig_path = path.replace(self._orig_format, self._target_format)
        self._conv_audio = self._audio_raw.export(self._conv_path, format=self._target_format)
        self.resample_audio()
        return self._conv_path

    def resample_audio(self):
        data, samplerate = librosa.load(self._orig_path)
        data_16k = librosa.resample(data, orig_sr=samplerate, target_sr=16000)
        path_parts = self._orig_path.split('.')
        path = path_parts[0] + '_16K' + '.' + path_parts[1]
        self.set_conv_path(path)
        soundfile.write(self._conv_path, data_16k, 16000, format=self._target_format)

    def librosa_resample_n_split(self, path: str):
        audio, sr = librosa.load(path)
        sr16 = 16000
        data_16k = librosa.resample(audio, orig_sr=sr, target_sr=sr16)
        buffer = 6 * sr16

        samples_total = len(data_16k)
        samples_wrote = 0
        counter = 1

        dir_path = path.split('.')[0] + '/'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        slices = []
        while samples_wrote < samples_total:

            # check if the buffer is not exceeding total samples
            if buffer > (samples_total - samples_wrote):
                buffer = samples_total - samples_wrote

            block = data_16k[samples_wrote: (samples_wrote + buffer)]
            out_filename = "split_" + str(counter) + "_" + path

            # Write 6 second segment
            full_path = dir_path + out_filename
            soundfile.write(full_path, block, sr16, format='flac')
            slices.append(full_path)
            counter += 1
            samples_wrote += buffer

        return slices



    def slice_audio(self, duration=6, target_format='flac'):
        seconds = duration * 1000
        length = self._conv_audio.duration_seconds

        slice_nr = length // duration
        slices = []
        for i in range(slice_nr):
            beg = i * seconds
            end = beg + seconds
            if i == 0:
                slices.append(self._conv_audio[:seconds])
            elif i == slice_nr - 1:
                slices.append(self._conv_audio[beg:])
            else:
                slices.append(self._conv_audio[beg:end])

        return self.safe_slices(slices, target_format=target_format)

    def safe_slices(self, slices: list, target_format='flac'):
        dir_path = self._conv_path.split('.')[0] + '/'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        path_list = []
        for i, a_slice in enumerate(slices):
            store_path = dir_path + 'slice' + str(i+1) + target_format
            path_list.append(store_path)
            a_slice.export(store_path, fomate=target_format)

        return path_list
