import whisper
import os


class WhisperService:
    def __init__(self, model_type="large", device='cuda:0'):
        self.model = whisper.load_model(model_type, device=device)

    def transcript(self, audio_file):
        # import ipdb; ipdb.set_trace()
        audio = whisper.load_audio(audio_file)
        audio = whisper.pad_or_trim(audio)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio, n_mels=128).to(self.model.device)
        # detect the spoken language
        _, probs = self.model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")
        # decode the audio
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        return result.text

    def transcript_file(self, audio):
        pass