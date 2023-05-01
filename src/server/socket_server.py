import os
import socket
import json
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get('IP')
PORT = int(os.environ.get('SSL_PORT'))

BUFFER_SIZE = 296
remainingTrack = ''
stream = ''
string = ''
active_source = None
last_time_stamp = 0


def create_json(x=None, y=None, z=None):
    sounds_dict = {
        "sounds": [
            {
                "direction": {"x": x, "y": y, "z": z},
                "type": "VOICE"
            }
        ]
    }

    print(sounds_dict)
    with open(os.environ.get('PATH_TO_JSON_FILE'), 'w') as outfile:
        json.dump(sounds_dict, outfile)

def create_json_with_energy(x=None, y=None, z=None, e=None):
    sounds_dict = {
        "sounds": [
            {
                "direction": {"x": x, "y": y, "z": z, "e":e},
                "type": "VOICE"
            }
        ]
    }

    print(sounds_dict)
    with open(os.environ.get('PATH_TO_JSON_FILE'), 'w') as outfile:
        json.dump(sounds_dict, outfile)

def processSSL(msg):
    global active_source
    global last_time_stamp
    data = ''
    try:
        data = json.loads(msg)
        # TODO iterate over 4 energy sources and compute mean for better accuracy?
        active_source = data['src'][0]

        if active_source['E'] > 0.3:
            last_time_stamp = data['timeStamp']
            x = active_source['x']
            y = active_source['y']
            z = active_source['z']
            e = active_source['E']
            create_json(x, y, z)
    
        elif data['timeStamp'] - last_time_stamp > 100:
            print(data['timeStamp'] - last_time_stamp)
            active_source = None
            create_json()

    except:
        pass



def processSST(msg):
    global active_source
    data = ''
    try:
        data = json.loads(msg)
        for source in data['src']:
            
            if source['activity'] > 0.6:
                if not active_source:
                    if source['id'] != 0:
                        active_source = source
                    
                elif source['id'] is active_source['id']:
                    active_source = source

                elif source['id'] is not active_source['id']:
                    if source['activity'] > active_source['activity']:
                        active_source = source
                        
                x = active_source['x']
                y = active_source['y']
                z = active_source['z']
                create_json(x, y, z)
                
            else:
                active_source = None
                create_json()

    except:
        pass

def server():
    remainingTrack = ''
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST,PORT))
    server_socket.listen(5)

    print("Listening on %s:%s..." % (HOST, str(PORT)))
    conn, addr = server_socket.accept()
    print(f'Connected to {addr}')

    while True:
        data = conn.recv(BUFFER_SIZE).decode()
        if not data:
            print("No data")
            break

        stream = remainingTrack + data
        strs = stream.split("}\n{")

        if (len(strs) < 2):
            remainingTrack = stream

        for index, string in enumerate(strs):
            if len(string) > 0:
                if(index == len(strs)-1):
                    remainingTrack = string

                if (string[0] != '{'):
                    string = '{' + string
                
                if (string[len(string)-2] != '}'):
                    if(string[len(string)-3] != '}'):
                        string = string + '}'

        processSSL(string)


if __name__ == '__main__':
    server()
