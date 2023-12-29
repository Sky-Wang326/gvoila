import time
import os
import requests
import pandas as pd
import json
from GazeUtils import Gaze2Fixation
from utils import csvLogger, calculate_blurriness
from moviepy.editor import VideoFileClip, imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class QueryProcessorGPT4V:
    def __init__(self, request_url):
        self.request_url = request_url

    def query(self, query_folder):
        for file in ["audio.wav", "gaze_data.json", "video.mp4", "video_timestamp.json"]:
            if not os.path.isfile(os.path.join(query_folder, file)):
                raise FileNotFoundError(f"The {file} is missing.")
        
        # ------------ calculate fixation ------------
        with open (os.path.join(query_folder, "gaze_data.json"), "r") as f:
            gaze_data = json.load(f)
        video_timestamp = [t*1000 for t in json.load(open(os.path.join(query_folder, "video_timestamp.json"), "r"))]
        cleaned_gaze_data = [(p[0], p[1], p[3]*1000) for p in gaze_data if p[3] * 1000 >= video_timestamp[0] and p[3] * 1000 <= video_timestamp[-1]]
        fixations = Gaze2Fixation.simpleDispersionBased(cleaned_gaze_data)
        csvLogger(["start_idx", "end_idx", "duration[ms]", "start_time", "end_time"], fixations, os.path.join(query_folder, "fixations.csv"))
        
        
        
        # ------------ choose video frame and gaze points ------------
        video = VideoFileClip(os.path.join(query_folder, "video.mp4"))
        width, height = video.size
        fps = round(video.fps)
        gaze_points = {"points": []}
        fix_maxidx = np.sort(np.argsort([f[2] for f in fixations])[-3:])
        print("fix_maxidx: ", fix_maxidx)
        
        for idx in fix_maxidx:
            fix_start = fixations[idx][3]
            fix_end = fixations[idx][4]
            print(f"fix_start: {fix_start}, fix_end: {fix_end}")
            frames = []
            for frame_idx in range(len(video_timestamp)):
                if video_timestamp[frame_idx] >= fix_start and video_timestamp[frame_idx] <= fix_end:
                    frame = video.get_frame(frame_idx/fps)
                    frames.append((frame_idx, frame, calculate_blurriness(frame)))
            best_frame = max(frames, key=lambda x: x[2])
            if best_frame[2] < 100:
                print("blurry: ", best_frame[2])
            imageio.imwrite(os.path.join(query_folder, f"fixation_{idx}.png"), best_frame[1])
            frame_gaze = [(p[0], p[1]) for p in cleaned_gaze_data if p[2] >= fix_start and p[2] <= fix_end]
            gaze_points["points"].append([[np.mean([p[0] for p in frame_gaze]) / width, np.mean([p[1] for p in frame_gaze]) / height]])
        gaze_path = os.path.join(query_folder, "query_gaze.json")
        json.dump(gaze_points, open(gaze_path, "w"))
        
        # ------------ send request ------------
        image_files = []
        for image_path in os.listdir(query_folder):
            if image_path.endswith(".png"):
                image_path_n = os.path.join(query_folder, image_path)
                image_files.append(("images", (image_path_n, open(image_path_n, "rb"), "image/png")))
        audio_path = os.path.join(query_folder, "audio.wav")
        
        with open (audio_path, "rb") as audio_file, open (gaze_path, "r") as gaze_file:
            file = image_files + [
                ("audio", (audio_path, audio_file, "audio/mpeg")),
                ("json", (gaze_path, gaze_file, "application/json")),
            ]
            print(self.request_url)
            # print(file)
            response = requests.post(self.request_url, files=file)
            print(response)
            # print(f"Time taken for the request: {time.time() - start_time} seconds")
            responses = response.json()
            if "error" in responses:
                print("ERROR!!! ------------ \n", responses)
                return
            with open (os.path.join(query_folder, "response.json"), "w") as f:
                json.dump(responses, f, ensure_ascii=False, indent=4)
            # print("response: ", responses)
            return responses
        
        
        

if __name__ == "__main__":
    qp = QueryProcessorGPT4V("http://127.0.0.1:5000/api/voila-4v")
    qp.query("data/1703624937.443079")
