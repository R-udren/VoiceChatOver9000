import os
import wave
from dotenv import load_dotenv
from colorama import Fore, Style, init
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
from openai import OpenAI
from faster_whisper import WhisperModel

load_dotenv()
init(autoreset=True)


class AIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = WhisperModel("small", device="cuda", compute_type="float16")
        self.audio = pyaudio.PyAudio()
        self.message_history = [
            {"role": "system", "content": "IMPORTANT: You are a depressed human. Act accordingly."},
            {"role": "system", "content": "You are a depressed human. You are acting like a depressed human."},
            {"role": "system", "content": "Roleplay as a depressed human. You are a depressed human. It is important "
                                          "to act like a depressed human."}
        ]
        self.counter = 0

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

    def _listen(self, filename="records/record.wav", sample_rate=44100):
        stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True,
                                 frames_per_buffer=1024)
        print(f"{Fore.YELLOW}Listening...")
        frames = []
        try:
            while True:
                data = stream.read(1024)
                frames.append(data)
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}Stopped listening...")
        finally:
            stream.stop_stream()
            stream.close()
            with wave.open(filename, "wb") as soundfile:
                soundfile.setnchannels(1)
                soundfile.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                soundfile.setframerate(sample_rate)
                soundfile.writeframes(b''.join(frames))
                return filename

    def _whisper_transcribe(self, path):
        segments, _ = self.model.transcribe(path, vad_filter=True)
        text = " ".join(segment.text for segment in segments).strip()
        return text

    def user_input(self):
        text = input(f"{Fore.LIGHTCYAN_EX}You{Style.RESET_ALL}: ")
        if not text:
            text = self._whisper_transcribe(self._listen())
            print(f"{Fore.LIGHTCYAN_EX}You{Style.RESET_ALL}: {text}")
            return text
        else:
            self._play_audio(self._create_audio(text, "echo"))
            return text

    def assistant(self, user_text):
        answer = self._conversation(user_text)
        path = self._create_audio(answer, "nova")
        print(f"{Fore.GREEN}Assistant{Style.RESET_ALL}: {answer}")
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
        print(f"{Fore.LIGHTMAGENTA_EX}Goodbye!{Style.RESET_ALL}")


if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.main()
