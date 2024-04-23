import os
from typing import Literal

from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAI, APIConnectionError

from audio_utils import AudioUtils
import config


class AIAssistant:
    def __init__(self, console, openai_client):
        self.console: Console = console
        self.audio: AudioUtils = AudioUtils()
        self.client: OpenAI = openai_client
        self.counter = 0
        self.legend = config.LEGEND

        self.message_history = [
            {"role": "system", "content": self.legend},
            {"role": "system", "content": f"You are chatting with USER! the Username is: {os.getlogin()}"},
            {"role": "user", "content": f"My name is {os.getlogin()}."},
            {"role": "assistant", "content": "I see..."}
        ]

    def speech_to_text(self, audio_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"File not found: {audio_path}")

        audio_file = open(audio_path, "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text

    def text_to_speech(self, text, voice: Literal["nova", "echo"] = "nova"):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        self.counter += 1
        path = f"{config.RECORDS_DIR}/{voice}_{self.counter}_response.mp3"
        response.write_to_file(path)
        return path

    def conversation(self, user_input):
        self.message_history.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.message_history,
        )
        answer = response.choices[0].message.content
        self.message_history.append({"role": "assistant", "content": answer})
        return answer

    def user_input(self):
        text = self.console.input("\n[bright_cyan]You[bright_white]: ")
        if not text:
            with self.console.status(":microphone:[bright_yellow] Recording... (CTRL+C to Stop)", spinner="point"):
                audio_path = self.audio.record_mic()
            with self.console.status(":loud_sound:[bright_green] Transcribing...", spinner="arc"):
                text = self.speech_to_text(audio_path)
            self.console.print(f"\n[bright_cyan]You[bright_white]: {text}")
            return text
        else:
            self.audio.play_audio(self.text_to_speech(text, "echo"))
            return text

    def assistant(self, user_text):
        with self.console.status(":robot:[bright_green] Thinking...", spinner="point"):
            answer = self.conversation(user_text)
            path = self.text_to_speech(answer, "nova")
            md = Markdown(answer)
        self.console.print(f"[bold bright_green]Assistant[bright_white]: ", end="")
        self.console.print(md)

        self.audio.play_audio(path)
        return answer

    def main(self):
        try:
            while True:
                user_text = self.user_input()
                if not user_text:
                    continue
                self.assistant(user_text)
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n\n:keyboard:[red] Interrupted by user.")
        except FileNotFoundError as fe:
            self.console.print(f":floppy_disk:[red] FileNotFoundError:[white] {fe}")
        except APIConnectionError as ace:
            self.console.print(f":satellite:[red] APIConnectionError:[white] {ace}\n\n"
                               f"[bright_red]Please check your internet connection or proxy.")
        except Exception as e:
            self.console.print_exception(show_locals=False)
        finally:
            self.shutdown()

    def shutdown(self):
        del self.audio
        self.console.print("\n[bold bright_yellow]Goodbye!:wave:")
        exit()
