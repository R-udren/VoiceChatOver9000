import httpx
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from openai import OpenAI

from ai_assistant import AIAssistant
from config import OPENAI_API_KEY, PROXY_URL


def main():
    console = Console(style="bold bright_white", markup=True)
    http_client = None
    if PROXY_URL:
        http_client = httpx.Client(
            proxies={"http://": PROXY_URL, "https://": PROXY_URL},
            transport=httpx.HTTPTransport(retries=3, local_address="0.0.0.0")
        )
    openai = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
    assistant = AIAssistant(console, openai)

    console.clear()
    console.print(Panel.fit("[bright_magenta]:wave: Welcome to the rovert's AI Assistant chat!\n\n"
                            "[bright_yellow]:information:  Empty input will trigger the microphone.\n\n"
                            "[bright_red]:exclamation: Press CTRL+C to exit.",
                            border_style="bold blue", title="AI Assistant"))

    assistant.main()


if __name__ == "__main__":
    main()
