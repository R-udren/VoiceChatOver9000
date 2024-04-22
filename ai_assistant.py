import os
from typing import Literal

from rich.console import Console
from openai import OpenAI

from audio_utils import AudioUtils
from console_utils import fancy_printer
import config


class AIAssistant:
    def __init__(self, console, openai_client):
        self.console: Console = console
        self.audio: AudioUtils = AudioUtils()
        self.client: OpenAI = openai_client
        self.counter = 0
        self.legend = config.LEGEND

        self.message_history = [
            {
                "role": "system", "content": self.legend
            }
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
        text = self.console.input("\n[cyan]You[white]: ")
        if not text:
            with self.console.status(":microphone:[bright_yellow] Recording...", spinner="point"):
                audio_path = self.audio.record_mic()
            with self.console.status(":loud_sound:[green] Transcribing...", spinner="arc"):
                text = self.speech_to_text(audio_path)
            if config.FANCY_WRITE:
                fancy_printer(text)
            else:
                self.console.print(text, style="white")
            return text
        else:
            self.audio.play_audio(self.text_to_speech(text, "echo"))
            return text

    def assistant(self, user_text):
        with self.console.status(":robot:[green] Thinking...", spinner="point"):
            answer = self.conversation(user_text)
            path = self.text_to_speech(answer, "nova")
        self.console.print("[bold green]Assistant[white]: ", end="")
        if config.FANCY_WRITE:
            fancy_printer(answer)
        else:
            self.console.print(answer, style="white")
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
            self.console.print(f":floppy_disk:[red] Error: {fe}")
        except Exception as e:
            self.console.print_exception(show_locals=True)
        finally:
            self.shutdown()

    def shutdown(self):
        del self.audio
        self.console.print("\n[bold yellow]Goodbye!:wave:")
        exit()
