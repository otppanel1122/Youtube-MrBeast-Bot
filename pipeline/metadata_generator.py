import os
import json
import random
import requests
from pipeline.config import GEMINI_API_KEY

HOOK_TEMPLATES = [
    "WAIT TILL THE END! 😱",
    "CAN HE REALLY DO THIS?! 🤯",
    "HE ALMOST LOST EVERYTHING! 💸",
    "THIS WAS UNREAL! 🚨",
    "WOULD YOU DO THIS FOR $500K? 🤔",
    "I DID NOT EXPECT THAT! 🔥"
]

def generate_metadata(video_title, segment_name):
    hook_text = random.choice(HOOK_TEMPLATES)
    
    # Clean base title
    clean_title = video_title.split("|")[0].strip()
    
    # Default high-CTR title
    short_title = f"{clean_title.upper()} 😱 #Shorts #MrBeast"
    if len(short_title) > 90:
        short_title = f"{clean_title[:60].upper()} 😱 #Shorts #MrBeast"
        
    description = (
        f"{clean_title}\n\n"
        f"The most insane moments from MrBeast! Would you attempt this challenge? "
        f"Comment below who was your favorite!\n\n"
        f"#MrBeast #Shorts #Challenge #Viral #Gaming #Extreme #Trending"
    )
    
    tags = [
        "mrbeast", "mrbeast shorts", "challenge", "shorts", "viral",
        "extreme challenge", "win cash", "insane", "mrbeast challenge",
        "mrbeast gaming", "tiktok viral", "youtube shorts"
    ]
    
    if not GEMINI_API_KEY:
        return {"title": short_title, "description": description, "tags": tags, "hook": hook_text}
        
    prompt = f"""
You are a YouTube Shorts viral growth specialist.
Generate viral click-worthy YouTube Shorts metadata for a clip from this MrBeast video:
Original Title: "{video_title}"
Clip Type: {segment_name}

Return ONLY valid JSON with:
{{
  "title": "EMOJI + VIRAL HOOK TITLE (Max 80 chars) #Shorts #MrBeast",
  "hook": "ENGAGEMENT HOOK TEXT (Max 28 chars, uppercase, emoji)",
  "description": "Engaging description with emojis, questions for comments, and hashtags",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]
}}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.85, "response_mime_type": "application/json"}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            res = json.loads(text)
            print(f"[Metadata] Generated: '{res.get('title')}'")
            return res
    except Exception as e:
        print(f"[Metadata] Using fallback metadata: {e}")
        
    return {"title": short_title, "description": description, "tags": tags, "hook": hook_text}
