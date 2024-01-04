import os
import tempfile
from flask import Flask, request, jsonify, Response, stream_with_context
from sam_service.service import SAMService
from whisper_service.service import WhisperService
from gvoila_gpt4v_agent import GvoilaAgent

import json
# from PIL import Image
import cv2
import numpy as np
import time
import argparse
import base64

app = Flask(__name__)
agent = GvoilaAgent()
sam_service = SAMService("vit_h", device="cuda:0")
whisper_service = WhisperService(device="cuda:0")

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


@app.route('/api/voila-4v', methods=['POST'])
def voila_4v():
    try:
        start_time = time.time()
        if not request.files.getlist('images'):
            return jsonify({"error": "Invalid request. Please send an audio data."}), 400

        images = request.files.getlist('images')
        audio = request.files['audio']
        jsonfile = request.files['json']
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_json:
            jsonfile.save(temp_json.name)
            temp_json_path = temp_json.name

        with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
            audio.save(temp_audio.name)
            temp_audio_path = temp_audio.name
            
        query = whisper_service.transcript(temp_audio_path)
        print(f"{time.time() - start_time} seconds: ", query)
        
        temp_images_path = []
        visual_search_results = []
        for image in images:
            with tempfile.NamedTemporaryFile(delete=False) as temp_image:
                image.save(temp_image.name)
                temp_image_path = temp_image.name
                temp_images_path.append(temp_image_path)

        input_data = json.load(open(temp_json_path))
        content_info = [{
            "type": "text",
            "text": query
        }]
        for i, temp_image_path in enumerate(temp_images_path):
            image = cv2.imread(temp_image_path)
            height, width, _ = image.shape
            gaze_point = [[input_data["points"][i][0][0] * width, input_data["points"][i][0][1] * height]]
            sam_boxes = sam_service.get_attention(image, np.array(gaze_point), nums=1)[-1]
            sam_boxes = [int(x) for x in sam_boxes]
            print("sam", sam_boxes)
            cv2.rectangle(image, (sam_boxes[0], sam_boxes[1]), (sam_boxes[2], sam_boxes[3]), (0, 0, 255), 4)
            cv2.imwrite("test.png", image)
            base64_image = encode_image("test.png")
            content_info.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "high"
                }
            })
            
        response = agent.run(content_info)
        print(response)
        return jsonify(response), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error."}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
