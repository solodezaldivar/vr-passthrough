import os
import socket
import json 
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get('IP')
PORT = os.environ.get('PORT')
BUFFER_SIZE = 296
remainingTrack = ''
stream = ''
string = ''
active_source_id = ''

def create_json(x,y,z):
    sounds_dict = {
        "sounds": [
            {
                "direction": {"x": x,"y": y,"z": z},
            "type":"VOICE"
            }
        ]
    }
    print(sounds_dict)
    with open(os.environ.get('PATH_TO_JSON_FILE'), 'w') as outfile:
        json.dump(sounds_dict, outfile)

def process(msg):
    data = ''
    active_source_id = ''
    
    try:
        data = json.loads(msg)
        for source in data['src']:
            if  active_source_id == '':
                if source['id'] != 0:
                    active_source = source
                    break
            
            elif source['id'] == active_source['id']:
                continue

            elif source['id'] is not active_source['id']:
                if source['activity'] > active_source['activity']:
                    active_source = source
        x = active_source['x']
        y = active_source['y']
        z = active_source['z']

        create_json(x,y,z)
    except:
        print("ERROR:JSON LOADS")

def min_len(strs):
    if (len(strs) < 2):
            remainingTrack = stream
            return

def remaining(strs):
    for index, string in enumerate(strs):
            if(index == len(strs)-1):
                remainingTrack = string
                return
            
            if (string[0] != '{'):
                string = '{' + string
            

            if (string[len(string)-2] != '}'):
                if(string[len(string)-3] != '}'):
                    string = string + '}'

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

                process(string)

if __name__ == '__main__':
     server()
