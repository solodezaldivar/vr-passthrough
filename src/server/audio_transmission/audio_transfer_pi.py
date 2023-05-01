

import json
import pickle
import socket
import struct
import base64

import pyaudio

IP = "172.20.10.2"
PORT = 9566
FORMAT = pyaudio.paInt16
CHANNELS = 2
CHUNK = 1024
RATE = 16000

audio = pyaudio.PyAudio()
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket.connect((IP, PORT))





stream = audio.open(format=FORMAT,
                    channels=2,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

try:
    frames = []
    print("* echoing")
    print("Press CTRL+C to stop")
    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        if len(frames)>0:
            pickle_data = pickle.dumps(frames.pop(0))
            socket.sendall(pickle_data)

#            stream.write(frames.pop(0),CHUNK)
#        if len(frames) >= 10:
#            try:
#                pickle_data = pickle.dumps(frames)
#                socket.send(pickle_data)
#
#            except Exception as e:
#                print(e)
#                break
#            frames = []
except KeyboardInterrupt:
    print("* done echoing")
    pass

finally:
    if frames:
        try:
            pickle_data =  pickle.dumps(frames)
            socket.send(pickle_data)
        except Exception as e:
            print(e)

    print("* done echoing")

    stream.stop_stream()
    stream.close()
    audio.terminate()






# import os
# import pickle
# import socket
# import struct
# import wave

# import pyaudio

# RESPEAKER_RATE = 16000
# RESPEAKER_CHANNELS = 2 
# RESPEAKER_WIDTH = 2
# # run getDeviceInfo.py to get index
# RESPEAKER_INDEX = 1  # refer to input device id
# CHUNK = 1024
# RECORD_SECONDS = 5
# WAVE_OUTPUT_FILENAME = "output.wav"
# HOST = os.environ.get('IP')
# PORT = 1234


# p = pyaudio.PyAudio()

# stream = p.open(
#             rate=RESPEAKER_RATE,
#             format=p.get_format_from_width(RESPEAKER_WIDTH),
#             channels=RESPEAKER_CHANNELS,
#             input=True,
#             input_device_index=RESPEAKER_INDEX,)

# print("* recording")

# s = socket.socket()
# s.bind((HOST, (PORT-1)))


# frames = []

# for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     frames.append(data)
#     a = pickle.dumps(data)
#     message = struct.pack("Q",len(a))+a
#     s.sendall(message)


# print("* done recording")

# stream.stop_stream()
# stream.close()
# p.terminate()

# wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# wf.setnchannels(RESPEAKER_CHANNELS)
# wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
# wf.setframerate(RESPEAKER_RATE)
# wf.writeframes(b''.join(frames))
# wf.close()