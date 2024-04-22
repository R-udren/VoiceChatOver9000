from time import sleep
import sys


def typewritten_text(text):
    lines = text.split("\n")
    for line in lines:
        for char in line:
            print(char, end="")
            sys.stdout.flush()
            if char == " ":
                sleep(0.01)
            elif char in [",", ".", "!", "?"]:
                sleep(0.1)
            else:
                sleep(0.075)
        print()
        sleep(0.2)


if __name__ == "__main__":
    typewritten_text(
        "Hello! I am a text-to-speech assistant. "
        "I can help you with your daily tasks.\n"
        "How can I help you today?"
    )
