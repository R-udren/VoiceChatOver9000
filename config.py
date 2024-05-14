import logging
import os

import httpx
from dotenv import load_dotenv
from rich.logging import RichHandler

load_dotenv()


class Config:
    def __init__(self):
        self.SAMPLE_RATE = 44100
        self.CHANNELS = 1
        self.RECORDS_DIR = "records"

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        self.PROXY_URL = self.__proxy_url()
        self.HTTPX_CLIENT = self.__httpx_client()
        self.LEGEND = self.__legend()

    @staticmethod
    def __proxy_url():
        proxy_url = os.getenv("PROXY_URL")
        return proxy_url

    def __legend(self):
        legend = ""
        if os.path.exists("legend.txt"):
            with open("legend.txt", "r", encoding="utf-8") as file:
                self.LEGEND = file.read()
        return legend

    def __httpx_client(self):
        http_client = None
        if self.PROXY_URL:
            http_client = httpx.Client(
                proxies={"http://": self.PROXY_URL, "https://": self.PROXY_URL},
                transport=httpx.HTTPTransport(retries=3, local_address="0.0.0.0")
            )
        return http_client


def setup_logger(log_level: int = logging.INFO):
    log = logging.getLogger(__name__)
    log.setLevel(log_level)

    time_format = "%H:%M:%S"
    log_format = "[{asctime}] [{module:^8}] [{levelname:^8}] {message}"

    # Formatters
    formatter = logging.Formatter("%(message)s")
    file_formatter = logging.Formatter(log_format, style="{", datefmt=time_format)

    # Handlers
    rich_handler = RichHandler(show_time=True, rich_tracebacks=True, log_time_format=time_format)
    rich_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("output.log")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Add handlers
    log.addHandler(rich_handler)
    log.addHandler(file_handler)

    return log
