import pyaudio
import socket
import signal
import subprocess
import sys
from threading import Thread
HOST = "172.20.10.2"
PORT = 9566
frames = []


ODAS_BIN_PATH = '../odas/build/bin/odaslive'
CONFIG_FILE = '../odas/build/bin/home.cfg'

odas_process = subprocess.Popen([ODAS_BIN_PATH, '-c', CONFIG_FILE])

def udpStream():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if len(frames) > 0:
            udp.sendto(frames.pop(0), (HOST, PORT))

    udp.close()

def record(stream, CHUNK):
    while True:
        audio_data = stream.read(CHUNK)
        odas_process.stdin.write(audio_data)
        frames.append(stream.read(audio_data))

def signal_handler(signal, frame):
    print("Exiting...")
    sys.exit(0)


if __name__ == "__main__":
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = CHUNK,
                    )
    Tr = Thread(target=record, args=(stream, CHUNK,))
    Ts = Thread(target=udpStream)
    Tr.daemon = True  # Set the threads as daemon threads
    Ts.daemon = True

    signal.signal(signal.SIGINT, signal_handler)

    Tr.start()
    Ts.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Exiting...")

    sys.exit(0)
