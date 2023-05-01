import json
import os
import pickle
import socket
import struct
import sys

import pyaudio
from dotenv import load_dotenv

load_dotenv()

HOST = "172.20.10.2"
PORT = 9566

IP = "172.20.10.2"
PORT = 9566
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


# # Welcome to PyShine
# # This is client code to receive video and audio frames over TCP

# import socket,os
# import threading, wave, pyaudio, pickle,struct
# host_name = socket.gethostname()
# host_ip = '172.20.10.3'#  socket.gethostbyname(host_name)
# print(host_ip)
# port = 9611
# def audio_stream():

# 	p = pyaudio.PyAudio()
# 	CHUNK = 1024
# 	stream = p.open(format=p.get_format_from_width(2),
# 					channels=2,
# 					rate=44100,
# 					output=True,
# 					frames_per_buffer=CHUNK)

# 	# create socket
# 	client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# 	socket_address = (host_ip,port-1)
# 	print('server listening at',socket_address)
# 	client_socket.connect(socket_address)
# 	print("CLIENT CONNECTED TO",socket_address)
# 	data = b""
# 	payload_size = struct.calcsize("Q")
# 	while True:
# 		try:
# 			while len(data) < payload_size:
# 				packet = client_socket.recv(4*1024) # 4K
# 				if not packet: break
# 				data+=packet
# 			packed_msg_size = data[:payload_size]
# 			data = data[payload_size:]
# 			msg_size = struct.unpack("Q",packed_msg_size)[0]
# 			while len(data) < msg_size:
# 				data += client_socket.recv(4*1024)
# 			frame_data = data[:msg_size]
# 			data  = data[msg_size:]
# 			frame = pickle.loads(frame_data)
# 			stream.write(frame)

# 		except:

# 			break

# 	client_socket.close()
# 	print('Audio closed')
# 	os._exit(1)

# t1 = threading.Thread(target=audio_stream, args=())
# t1.start()


