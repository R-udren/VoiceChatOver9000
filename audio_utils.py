import os
import threading
import wave
from typing import Optional

import pyaudio
from pydub import AudioSegment
from pydub.playback import play

from config import cfg


class AudioUtils:
    def __init__(self):
        self.config = cfg

        self.sample_rate = self.config.SAMPLE_RATE
        self.channels = self.config.CHANNELS
        self.records_dir = self.config.RECORDS_DIR

        self.audio = pyaudio.PyAudio()
        self.lock = threading.Lock()
        self.playback_thread: Optional[threading.Thread] = None

        if not os.path.exists(self.records_dir):
            os.makedirs(self.records_dir)

    def play_audio_threaded(self, path):
        self.playback_thread = threading.Thread(
            target=self.play_audio, args=(path,), daemon=True
        )
        self.playback_thread.start()

    def stop_audio(self):
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join()

    def play_audio(self, path):
        with self.lock:
            if os.path.exists(path):
                audio = AudioSegment.from_file(path)
                play(audio)
            else:
                raise FileNotFoundError(f"File not found: {path}")

    def record_mic(self, filename="records/record.wav"):
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024,
        )
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
                soundfile.writeframes(b"".join(frames))
                return filename

    def __del__(self):
        self.audio.terminate()
