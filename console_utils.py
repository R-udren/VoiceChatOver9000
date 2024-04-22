import asyncio
import sys


async def fancy_printer(text):
    lines = text.split("\n")
    for line in lines:
        for char in line:
            print(char, end="")
            sys.stdout.flush()
            if char == " ":
                await asyncio.sleep(0.01)
            elif char in [",", ".", "!", "?"]:
                await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.075)
        print()
        await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(fancy_printer(
        "Hello, I am a fancy printer. I will print this text with fancy effects.\n"
        "I will print this text with fancy effects. I will print this text with fancy effects."))
