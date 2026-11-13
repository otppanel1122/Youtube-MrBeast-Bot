import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PUTER_AUTH_TOKEN = os.getenv("PUTER_AUTH_TOKEN")
VIDEO_PRIVACY = os.getenv("VIDEO_PRIVACY", "public")
