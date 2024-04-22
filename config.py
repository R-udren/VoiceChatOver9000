import os

from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE = 44100
CHANNELS = 1
RECORDS_DIR = "records"

FANCY_WRITE = True

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

with open("legend.txt", "r") as file:
    LEGEND = file.read()