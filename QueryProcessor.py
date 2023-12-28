import time
import os
import requests
import pandas as pd
import json
from GazeUtils import Gaze2Fixation
from utils import csvLogger



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
        cleaned_gaze_data = [(p[0], p[1], p[3]*1000) for p in gaze_data]
        fixations = Gaze2Fixation.simpleDispersionBased(cleaned_gaze_data)
        csvLogger(["start_idx", "end_idx", "duration[ms]", "start_time", "end_time"], fixations, os.path.join(query_folder, "fixations.csv"))
        
        
  