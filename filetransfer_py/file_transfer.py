from flask import Flask, send_file

app = Flask(__name__)

@app.get("/directionFile/")
def get_file():
    try:
        return send_file("/Users/raffi07/coding/masterproject/filetransfer/test.json")
    except Exception as e:
        return str(e)

    