import json
import os
import pickle
import socket
import struct
import sys

import pyaudio
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get('IP')
PORT = os.environ.get('AUDIO_TRANSPORT_PORT')
FORMAT = pyaudio.paInt16
CHANNELS = 2
CHUNK = 1024
RATE = 16000

def getAudioDevices():
        for i in range(audio.get_device_count()):
            dev = audio.get_device_info_by_index(i)
            print((i,dev['name'],dev['maxOutputChannels'],dev['maxInputChannels']))

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT,
                    channels=2,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)

#TODO remove clicking sound - my best guess - we need to do smth about the CHUNK size
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print("Listening on %s:%s..." % (HOST, str(PORT)))
    conn, addr = server_socket.accept()
    print(f'Connected to {addr}')
    data_buffer = b''
    while True:
        try:
            data = conn.recv(CHUNK)
            if not data:
                break
            stream.write(data)

            # data_buffer+=data

            # frames = pickle.loads(data_buffer)
            # for frame in frames:
            #     stream.write(frame)
            # data_buffer = b''

            # while len(data_buffer) >= 4:
            #     message_length = int.from_bytes(data_buffer[:4], byteorder='little')
            #     data_buffer = data_buffer[4:]

            #     if len(data_buffer) < message_length:
            #         break
            #     audio_data = data_buffer[:message_length]
            #     frames = pickle.loads(audio_data)
            #     for frame in frames:
            #         stream.write(frame)
            #     data_buffer = data_buffer[message_length:]
            # if len(data_buffer) >= CHUNK * CHANNELS * 2:
            #     frame = data_buffer[:CHUNK*CHANNELS*2]
            #     data_buffer = data_buffer[CHUNK * CHANNELS * 2:]
            #     frame = bytes(frame)
            #     stream.write(frame)
        except Exception as e:
            print(e)
            pass

if __name__ == '__main__':
    server()


