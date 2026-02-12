import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
