import asyncio
import pyaudio
import wave
from concurrent.futures import ThreadPoolExecutor




class AudioRecorder:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.audio = pyaudio.PyAudio()
        self.chunk = 1024
        self.wavstream = self.audio.open(format=pyaudio.paInt16,
                               channels=1,
                               rate=16000,
                               input=True,
                               frames_per_buffer=self.chunk)
        self.loop = asyncio.get_running_loop()
    
    async def read_buffer(self):
        return await self.loop.run_in_executor(self.executor, self.wavstream.read, self.chunk)
    
    def __del__(self):
        self.wavstream.stop_stream()
        self.wavstream.close()
        self.audio.terminate()
        
    @staticmethod    
    def save_wavefile(file_name, data) -> None:
        wavfile = wave.open(file_name, 'wb')
        wavfile.setnchannels(1)
        wavfile.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wavfile.setframerate(16000)
        for d in data:
            wavfile.writeframes(d)
        wavfile.close()
        


    async def iter_frame(self):
        while True:
            buffer = await self.read_buffer()
            yield buffer
