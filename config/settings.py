import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
GIGA_TOKEN = os.getenv("GIGA_TOKEN")
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")
MODEL = os.getenv("MODEL")