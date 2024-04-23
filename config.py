import os


from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE = 44100
CHANNELS = 1
RECORDS_DIR = "records"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_ADDRESS = os.getenv("PROXY_ADDRESS")
PROXY_URL = f"http://{PROXY_ADDRESS}" if PROXY_ADDRESS else None

LEGEND = ""

if os.path.exists("legend.txt"):
    with open("legend.txt", "r", encoding="utf-8") as file:
        LEGEND = file.read()