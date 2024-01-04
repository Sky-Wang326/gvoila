# G-VOILA: A Gaze-Facilitated Question Answering Assistant on Smart Glasses

<p align="center">
  <img src='https://avatars.githubusercontent.com/u/155179055?s=200&v=4' height=150> 
    <img src='./assets/gvoila.png' height=150>
</p>

## Overview 
With the advancement of wearable device and AI, querying with intelligent assistant anywhere and anytime is becoming a reality. We implement G-VOILA, a gaze-facilitated question answering assistant on smart glasses. With our code, G-VOILA can be reproduced with public available devices and resources.

![G-VOILA Framework](./assets/framework.png)

G-VOILA requires a PC to receive the data stream in realtime from smart glasses and process it. The preprocessed data were sent to a GPU server which runs a service to answer user's questions. The answer will be sent back to the PC and displayed to the user. 

## Components 1 - Agent Service (PC / GPU Server)
Code to setup the agent service on PC / GPU server is in [voila-service](./voila-service) folder. For requirements and setup, please refer to [voila-service/README.md](./voila-service/README.md).

[GPT-4v](https://platform.openai.com/docs/guides/vision) serves as the main visual language model to answer user's questions, one need to paste their own API key to use it. [Whisper](https://github.com/openai/whisper) is used to transcript the user's audio query to text. [SAM](https://github.com/facebookresearch/segment-anything) is used to crop the object of interest based on gaze points from the user's view. Both Whisper and SAM requires a GPU to run, yet one can substitute them with official API if GPU is not available.

## Components 2 - Smart Glasses (Pupil Lab Invisible)

## Components 3 - Query Trigger (Wireless Push Button)
