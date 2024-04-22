import os
import wave

import pyaudio
from dotenv import load_dotenv
from openai import OpenAI
from pydub.playback import play
from pydub import AudioSegment
from rich.console import Console

load_dotenv()
console = Console(style="bold cyan")


class AIAssistant:
    def __init__(self, sample_rate=44100, channels=1):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.audio = pyaudio.PyAudio()
        self.sample_rate = sample_rate
        self.channels = channels
        with open("legend.txt", "r") as file:
            self.legend = file.read()
        self.message_history = [
            {
                "role": "system", "content": self.legend
            }
        ]
        self.counter = 0

        # Create records directory
        if not os.path.exists("records"):
            os.makedirs("records", exist_ok=True)

    def _conversation(self, user_input):
        self.message_history.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.message_history,
        )
        answer = response.choices[0].message.content
        self.message_history.append({"role": "assistant", "content": answer})
        return answer

    def _create_audio(self, message, voice):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=message,
        )
        self.counter += 1
        path = f"records/{self.counter}_response.mp3"
        response.write_to_file(path)
        return path

    @staticmethod
    def _play_audio(path):
        sound = AudioSegment.from_file(path)
        play(sound)

    def _listen(self, filename="records/record.wav"):
        stream = self.audio.open(format=pyaudio.paInt16, channels=self.channels, rate=self.sample_rate, input=True,
                                 frames_per_buffer=1024)

        frames = []
        try:
            with console.status("Listening...", spinner="point"):
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

    def _whisper_transcribe(self, path):
        audio_file = open(path, "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text

    def user_input(self):
        text = console.input("You: ")

        if text.lower() == "exit":
            self.shutdown()
            return
        elif not text:
            text = self._whisper_transcribe(self._listen())
            console.print(f"You: {text}")
            return text
        else:
            self._play_audio(self._create_audio(text, "echo"))
            return text

    def assistant(self, user_text):
        answer = self._conversation(user_text)
        path = self._create_audio(answer, "nova")
        console.print(f"Assistant: {answer}")
        self._play_audio(path)
        return answer

    def main(self):
        try:
            while True:
                user_text = self.user_input()
                self.assistant(user_text)

        except (KeyboardInterrupt, EOFError):
            self.shutdown()

    def shutdown(self):
        self.audio.terminate()
        console.print("Goodbye!")


if __name__ == "__main__":
    assistant = AIAssistant()
    console.print("Welcome to the rovert's AI Assistant chat!\n"
                  "Empty input will trigger the microphone.\n"
                  "Press CTRL+C to exit.")
    assistant.main()
