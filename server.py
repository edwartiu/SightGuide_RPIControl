from flask import Flask, send_file, request
import os

app = Flask(__name__)

@app.route('/')
def new_image():
    processing_check = open("/home/edwartiu/SightGuide/processing.txt", "r").read().strip()
    if processing_check == "Image processing locally":
        return "Local"
    else:
        return "Remote"


@app.route('/get_image')
def get_image():
    response = send_file("/home/edwartiu/SightGuide/image.jpg", mimetype='image/jpg')
    os.remove("/home/edwartiu/SightGuide/image.jpg")
    return response



@app.route('/upload_audio', methods=['POST'])
def upload_response():
    audio_file = request.files['audio']
    audio_file.save("home/edwartiu/SightGuide/audio/speech.mp3")
    return "Audio file uploaded successfully."
