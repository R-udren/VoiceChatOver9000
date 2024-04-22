import httpx
from rich.console import Console
from rich.panel import Panel
from openai import OpenAI

from ai_assistant import AIAssistant
from config import OPENAI_API_KEY, PROXY_ADDRESS


console = Console(style="bold cyan")
openai = OpenAI(api_key=OPENAI_API_KEY,
                http_client=httpx.Client(
                    proxy=PROXY_ADDRESS,
                    transport=httpx.HTTPTransport(retries=3, local_address="0.0.0.0")
                ))


def main():
    assistant = AIAssistant(console, openai)

    console.clear()
    console.print(Panel.fit("[bright_magenta]:wave: Welcome to the rovert's AI Assistant chat!\n\n"
                            "[yellow]:information:  Empty input will trigger the microphone.\n\n"
                            "[red]:exclamation: Press CTRL+C to exit.", border_style="bold blue", title="AI Assistant"))

    assistant.main()


if __name__ == "__main__":
    main()
