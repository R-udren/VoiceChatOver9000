import os
from typing import Literal

from openai import OpenAI, APIConnectionError
from openai.types.chat_model import ChatModel
from rich.console import Console
from rich.markdown import Markdown

from audio_utils import AudioUtils
from config import Config


class AIAssistant:
    def __init__(self, console, openai_client, history_path: str = None):
        self.console: Console = console
        self.config: Config = Config()
        self.audio: AudioUtils = AudioUtils()
        self.client: OpenAI = openai_client

        # Models
        self.language_model: ChatModel = "gpt-4o"
        self.tts_model: Literal["tts-1", "tts-1-hd"] = "tts-1"
        self.stt_model: Literal["whisper-1"] = "whisper-1"

        self.voices = {"User": "alloy", "Assistant": "nova", "System": "echo"}

        # History
        self.history_path = history_path
        self.message_history = [
            {"role": "system", "content": self.config.LEGEND},
            {"role": "system", "content": f"You are chatting with USER! the Username is: {os.getlogin()}.for"
                                          f"Don't forget to use emojis to express yourself!"},
            {"role": "user", "content": f"My name is {os.getlogin()}. But don't call me in my name."},
            {"role": "assistant", "content": "I see..."}
        ]

        if not self.client.api_key:
            raise ValueError("OpenAI API key is not provided.")

    def speech_to_text(self, audio_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"File not found: {audio_path}")

        audio_file = open(audio_path, "rb")
        transcription = self.client.audio.transcriptions.create(
            model=self.stt_model,
            file=audio_file
        )
        return transcription.text

    def text_to_speech(self, text, voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"):
        response = self.client.audio.speech.create(
            model=self.tts_model,
            voice=voice,
            input=text,
        )
        path = os.path.join(self.config.RECORDS_DIR, f"{voice}_{self.counters[voice]}.mp3")
        response.write_to_file(path)
        return path

    def conversation(self, user_input):
        self.message_history.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model=self.language_model,
            messages=self.message_history,
        )
        answer = response.choices[0].message.content
        self.message_history.append({"role": "assistant", "content": answer})
        return answer

    def user_input(self):
        prompt = "[bright_green]You[bright_white]: "
        text = self.console.input(prompt)
        if not text or text.isspace():
            with self.console.status(":microphone:[bright_yellow] Recording... (CTRL+C to Stop)", spinner="point"):
                audio_path = self.audio.record_mic()
            with self.console.status(":loud_sound:[bright_magenta] Transcribing...", spinner="arc"):
                text = self.speech_to_text(audio_path)
            self.console.print(prompt + text)
            return text
        else:
            with self.console.status(":loud_sound:[bright_yellow] Speaking...", spinner="arc"):
                audio_path = self.text_to_speech(text, "echo")
                self.audio.play_audio_threaded(audio_path)
            return text

    def assistant_answer(self, user_text):
        with self.console.status(":robot:[bright_green] Thinking...", spinner="point"):
            answer = self.conversation(user_text)
            audio_path = self.text_to_speech(answer, "nova")

        self.console.print(Markdown("`Assistant`: " + answer, code_theme="dracula", inline_code_theme="dracula"))
        self.audio.play_audio_threaded(audio_path)
        return answer

    def main(self):
        try:
            while True:
                user_text = self.user_input()
                if user_text:
                    self.assistant_answer(user_text)
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n\n:keyboard:[red]  Interrupted by user.")
        except FileNotFoundError as fe:
            self.console.print(f":floppy_disk:[red]  FileNotFoundError:[white] {fe}")
        except APIConnectionError as ace:
            self.console.print(f":satellite:[red] APIConnectionError:[white] {ace}\n\n"
                               f"[bright_red]Please check your internet connection or proxy.")
        except Exception:
            self.console.print_exception(show_locals=False)
        finally:
            self.shutdown()

    def shutdown(self):
        del self.audio
        if self.history_path:
            with open(self.history_path, "a", encoding="utf-8") as file:
                for message in self.message_history:
                    file.write(f"{message['role']}: {message['content']}\n")
            self.console.print("\n[bold bright_yellow]Chat history saved to [bright_magenta]history.txt")

        self.console.print("\n[bold bright_yellow]Goodbye!:wave:")
        exit()
