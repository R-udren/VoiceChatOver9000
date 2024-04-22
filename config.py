import os

from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE = 44100
CHANNELS = 1
RECORDS_DIR = "records"

# FANCY_WRITE = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_ADDRESS = os.getenv("PROXY_ADDRESS")
PROXY_URL = f"http://{PROXY_ADDRESS}"

with open("legend.txt", "r", encoding="UTF-8") as file:
    LEGEND = file.read()