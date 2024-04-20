import os
import wave
from typing import Literal

from dotenv import load_dotenv
from colorama import Fore, Style, init
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
from openai import OpenAI
from faster_whisper import WhisperModel

load_dotenv()

init(autoreset=True)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
model = WhisperModel("small", device="cuda", compute_type="float16")
audio = pyaudio.PyAudio()

message_history = [
    {"role": "system", "content": "IMPORTANT: You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "system", "content": "You are a depressed human. Act accordingly."},
    {"role": "user", "content": "How are you?"},
    {"role": "assistant", "content": "I'm feeling a bit down today..."},
]

counter = 0


def _conversation(message_history, user_input):
    message_history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=message_history,
    )
    answer = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": answer})
    return answer


def _create_audio(message, voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=message,
    )
    global counter
    counter += 1
    path = f"records/{counter}_response.mp3"
    response.write_to_file(path)
    return path


def _play_audio(path):
    sound = AudioSegment.from_file(path)
    play(sound)


def _listen(filename="records/record.wav", sample_rate=44100):
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=1024)
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
            soundfile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            soundfile.setframerate(sample_rate)
            soundfile.writeframes(b''.join(frames))
            return filename


def _whisper_transcribe(path):
    segments, _ = model.transcribe(path, vad_filter=True)
    text = " ".join(segment.text for segment in segments).strip()
    return text


def user_input():
    text = input(f"{Fore.LIGHTCYAN_EX}You{Style.RESET_ALL}: ")
    if not text:
        text = _whisper_transcribe(_listen())
        print(f"{Fore.LIGHTCYAN_EX}You{Style.RESET_ALL}: {text}")
        return text
    else:
        _play_audio(_create_audio(text, "echo"))
        return text


def assistant(user_text):
    answer = _conversation(message_history, user_text)
    path = _create_audio(answer, "nova")
    print(f"{Fore.GREEN}Assistant{Style.RESET_ALL}: {answer}")
    _play_audio(path)
    return answer


def main():
    try:
        while True:
            user_text = user_input()
            assistant(user_text)

    except (KeyboardInterrupt, EOFError):
        shutdown()


def shutdown():
    audio.terminate()
    print(f"{Fore.LIGHTMAGENTA_EX}Goodbye!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
