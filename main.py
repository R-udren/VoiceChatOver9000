from rich.console import Console
from rich.panel import Panel

from ai_assistant import AIAssistant


def main():
    console = Console(style="bold bright_white", markup=True)
    assistant = AIAssistant(console=console, history_path="history.txt")
    console.set_alt_screen(enable=True)  # Experimental, sometime make weird things
    console.clear()
    console.print(
        Panel.fit(
            "[bright_magenta]:wave: Welcome to the rovert's AI Assistant chat!\n\n"
            "[bright_yellow]:information:  Empty input will trigger the microphone.\n\n"
            "[bright_red]:exclamation: Press CTRL+C to exit.",
            border_style="bold blue",
            title="AI Assistant",
        )
    )

    assistant.main()
    console.set_alt_screen(enable=False)


if __name__ == "__main__":
    main()
