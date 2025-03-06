import os
import re
from typing import Dict, Literal

from openai import APIConnectionError, NotFoundError, OpenAI
from openai.types.audio.speech_model import SpeechModel
from openai.types.audio_model import AudioModel
from openai.types.chat_model import ChatModel
from rich.console import Console
from rich.markdown import Markdown

from audio_utils import AudioUtils
from config import Config, cfg


class AIAssistant:
    def __init__(self, console: Console, history_path: str = None):
        self.console: Console = console
        self.audio: AudioUtils = AudioUtils()
        self.config: Config = cfg
        self.client: OpenAI = OpenAI(
            api_key=self.config.OPENAI_API_KEY, http_client=self.config.HTTPX_CLIENT
        )

        # Models
        self.language_model: ChatModel = "gpt-4o-mini"
        self.tts_model: SpeechModel = "tts-1"
        self.stt_model: AudioModel = "whisper-1"

        # Voices
        self.voices: Dict[
            Literal["User", "Assistant", "System"],
            Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        ] = {"User": "alloy", "Assistant": "nova", "System": "echo"}
        self._counters = {voice: 0 for voice in self.voices.values()}

        # History
        self.history_path = history_path
        self.message_history = [
            {"role": "system", "content": self.config.LEGEND},
            {
                "role": "system",
                "content": f"You are chatting with USER: {os.getlogin()}.\n"
                f"Don't forget to use emojis to express yourself!\n",
            },
        ]

        if not self.client.api_key:
            raise ValueError("OpenAI API key is not provided.")

    def speech_to_text(self, audio_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"File not found: {audio_path}")

        audio_file = open(audio_path, "rb")
        transcription = self.client.audio.transcriptions.create(
            model=self.stt_model, file=audio_file
        )
        return transcription.text

    def text_to_speech(
        self,
        text,
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova",
    ):
        response = self.client.audio.speech.create(
            model=self.tts_model,
            voice=voice,
            input=text,
        )
        path = os.path.join(
            self.config.RECORDS_DIR, f"{voice}_{self._counters[voice]}.mp3"
        )
        self._counters[voice] += 1
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
        if self.config.AI_LISTENS and (not text or text.isspace()):
            with self.console.status(
                ":microphone:[bright_yellow] Recording... (CTRL+C to Stop)",
                spinner="point",
            ):
                audio_path = self.audio.record_mic()

            with self.console.status(
                ":loud_sound:[bright_magenta] Transcribing...", spinner="arc"
            ):
                text = self.speech_to_text(audio_path)

            self.console.print(prompt + text)
        else:
            if self.config.USER_SPEAKS:
                with self.console.status(
                    ":loud_sound:[bright_yellow] Speaking...", spinner="arc"
                ):
                    audio_path = self.text_to_speech(
                        text, self.voices.get("User", "alloy")
                    )
                    self.audio.play_audio_threaded(audio_path)
        return text

    def assistant_answer(self, user_text):
        audio_path = ""
        with self.console.status(":robot:[bright_green] Thinking...", spinner="point"):
            answer = self.conversation(user_text)

            if answer and self.config.AI_SPEAKS:
                answer_without_code = re.sub(
                    r"```[\s\S]*?```",
                    "[Code Snippet...]",
                    answer,
                )
                audio_path = self.text_to_speech(
                    answer_without_code, self.voices.get("Assistant", "nova")
                )

        self.console.print(
            Markdown(
                "`Assistant`: " + answer,
                code_theme="dracula",
                inline_code_theme="dracula",
            )
        )

        if self.config.AI_SPEAKS and os.path.exists(audio_path):
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
        except NotFoundError as nfe:
            self.console.print(f":mag:[red] NotFoundError:[white] {nfe}")
        except APIConnectionError as ace:
            self.console.print(
                f":satellite:[red] APIConnectionError:[white] {ace}\n\n"
                f"[bright_red]Please check your internet connection or proxy."
            )
        except Exception:
            self.console.print_exception(max_frames=2)
            self.console.input("\n\n:warning:[red]  Press Enter to exit.")
        finally:
            self.shutdown()

    def shutdown(self):
        del self.audio  # is equivalent to self.audio.terminate()
        self.console.set_alt_screen(False)

        if self.history_path:
            with open(self.history_path, "a", encoding="utf-8") as file:
                for message in self.message_history:
                    file.write(f"{message['role']}: {message['content']}\n")
            self.console.print(
                f"[bold bright_yellow]Chat history saved to [bright_magenta]{self.history_path}"
            )
        self.console.print("[bold bright_yellow]Goodbye!:wave:")
        exit()
