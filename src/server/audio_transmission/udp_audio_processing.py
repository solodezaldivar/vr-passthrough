import pyaudio
import socket
import sys
import time
import signal
from threading import Thread
import json
import os
frames = []
HOST = "172.20.10.2"
PORT = 9566


def udpStream(CHUNK):

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((HOST, PORT))

    print("Listening on %s:%s..." % (HOST, str(PORT)))

    while True:
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(soundData)

    udp.close()


def play(stream, CHUNK):
    BUFFER = 10
    while True:
        # try:
        if len(frames) == BUFFER:
            while True:
                stream.write(frames.pop(0), CHUNK)
                write_to_json("letal")
        # except:
        #     continue


def signal_handler(signal, frame):
    print("Exiting...")
    sys.exit(0)


def write_to_json(prediction):
    with open('../filetransfer/coordintes.json', 'r') as file:
        json_file = json.load(file)
    json_file['sounds'][0]['type'] = prediction
    print('Prediction is: ', json_file['sounds'][0]['type'])
    
    # Save back to the file
    with open('../filetransfer/coordintes.json', 'w') as file:
        json.dump(json_file, file)


if __name__ == "__main__":
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK,
                    )

    Ts = Thread(target=udpStream, args=(CHUNK,))
    Tp = Thread(target=play, args=(stream, CHUNK,))
    Ts.daemon = True
    Tp.daemon = True

    def run_program():
        Ts.start()
        Tp.start()
        while True:
            time.sleep(1)

    signal.signal(signal.SIGINT, signal_handler)
    run_program()
