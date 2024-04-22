from rich.console import Console
from openai import OpenAI

from ai_assistant import AIAssistant
from config import OPENAI_API_KEY

console = Console(style="bold cyan")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def main():
    assistant = AIAssistant(console, openai_client)

    console.clear()
    console.print("[blue]:wave: Welcome to the rovert's AI Assistant chat!\n"
                  "[yellow]:information:  Empty input will trigger the microphone.\n"
                  "[red]:exclamation: Press CTRL+C to exit.")

    assistant.main()


if __name__ == "__main__":
    main()
