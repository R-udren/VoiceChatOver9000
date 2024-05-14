from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from ai_assistant import AIAssistant
from config import Config


def main():
    config = Config()
    console = Console(style="bold bright_white", markup=True)

    openai = OpenAI(api_key=config.OPENAI_API_KEY, http_client=config.HTTPX_CLIENT)
    assistant = AIAssistant(console, openai)

    console.clear()
    console.print(Panel.fit("[bright_magenta]:wave: Welcome to the rovert's AI Assistant chat!\n\n"
                            "[bright_yellow]:information:  Empty input will trigger the microphone.\n\n"
                            "[bright_red]:exclamation: Press CTRL+C to exit.",
                            border_style="bold blue", title="AI Assistant"))

    assistant.main()


if __name__ == "__main__":
    main()
