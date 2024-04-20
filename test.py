import wave
import pyaudio
from faster_whisper import WhisperModel







if __name__ == "__main__":
    segments, _ = model.transcribe(listen(), vad_filter=True)
    text = " ".join(segment.text for segment in segments).strip()
    print(text)

