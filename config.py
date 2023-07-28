import os
import dotenv

class Config:
    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.ACCESS_ID = os.getenv("ACCESS_ID")
        self.ACCESS_KEY = os.getenv("ACCESS_KEY")
        self.API_ENDPOINT = os.getenv("API_ENDPOINT")
        self.MQ_ENDPOINT = os.getenv("MQ_ENDPOINT")
        self.DEVICES = os.getenv("DEVICES")

settings = Config()