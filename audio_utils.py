import os
import wave
import pyaudio
from pydub import AudioSegment
from pydub.playback import play

from config import SAMPLE_RATE, CHANNELS, RECORDS_DIR


class AudioUtils:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.records_dir = RECORDS_DIR

        if not os.path.exists(self.records_dir):
            os.makedirs(self.records_dir)

        self.audio = pyaudio.PyAudio()

    @staticmethod
    def play_audio(path):
        if os.path.exists(path):
            audio = AudioSegment.from_file(path)
            play(audio)
        else:
            raise FileNotFoundError(f"File not found: {path}")

    def record_mic(self, filename="records/record.wav"):
        stream = self.audio.open(format=pyaudio.paInt16, channels=self.channels, rate=self.sample_rate, input=True,
                                 frames_per_buffer=1024)

        frames = []
        try:
            while True:
                data = stream.read(1024)
                frames.append(data)
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop_stream()
            stream.close()
            with wave.open(filename, "wb") as soundfile:
                soundfile.setnchannels(self.channels)
                soundfile.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                soundfile.setframerate(self.sample_rate)
                soundfile.writeframes(b''.join(frames))
                return filename

    def __del__(self):
        self.audio.terminate()