import os
from flask import Flask, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.get("/directionFile/")
def get_file():
    try:
        return send_file(os.environ.get('PATH_TO_DIRECTION_JSON_FILE'))
    except Exception as e:
        return str(e)


@app.get("/objectsFile/")
def get_objects():
    try:
        return send_file(os.environ.get('PATH_TO_CAMERA_JSON_FILE'))
    except Exception as e:
        return str(e)

