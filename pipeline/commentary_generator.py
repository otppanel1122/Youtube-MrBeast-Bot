import os
import sys
import re
import json
import random
import subprocess
import requests
from pipeline.config import GEMINI_API_KEY, PUTER_AUTH_TOKEN

VOICES = [
    "en-US-ChristopherNeural",
    "en-US-GuyNeural",
    "en-US-AndrewMultilingualNeural",
    "en-US-BrianNeural"
]

def clean_clip_title(clip_title):
    clean = re.sub(r'@[A-Za-z0-9_.]+', '', clip_title)
    clean = clean.split("|")[0].replace("#", "").strip()
    if not clean or len(clean) < 4:
        clean = "Insane MrBeast Challenge"
    return clean

def generate_via_puter(clean_title):
    if not PUTER_AUTH_TOKEN:
        return None
    try:
        prompt = (
            f"You are a YouTube Shorts viral growth specialist. "
            f"Write a 15-second exciting reaction commentary breakdown for MrBeast's challenge: '{clean_title}'. "
            f"Respond ONLY with valid JSON having keys: "
            f"'narration' (high-energy spoken script ~45 words), "
            f"'hook_headline' (short uppercase title max 25 chars), "
            f"'title' (viral Shorts title with #Shorts #MrBeast), "
            f"'question' (one question for comments)."
        )
        escaped_prompt = prompt.replace("'", "\\'").replace('"', '\\"')
        js_code = f"""
const {{ init }} = require('@heyputer/puter.js/src/init.cjs');
const puter = init('{PUTER_AUTH_TOKEN}');
puter.ai.chat('{escaped_prompt}', {{model: 'gpt-4o-mini'}}).then(r => {{
    const text = r.message ? r.message.content : r;
    console.log(text);
    process.exit(0);
}}).catch(e => {{
    process.exit(1);
}});
"""
        res = subprocess.run(["node", "-e", js_code], capture_output=True, text=True, timeout=20)
        if res.returncode == 0 and res.stdout.strip():
            raw = res.stdout.strip()
            # Clean markdown JSON fences if any
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            data = json.loads(raw)
            print("[Commentary] Generated via Puter AI (GPT-4o-mini) successfully!")
            return {
                "narration": data.get("narration"),
                "hook_headline": data.get("hook_headline", "CAN HE WIN?! 😱"),
                "title": data.get("title", f"{clean_title.upper()} 😱 #Shorts #MrBeast"),
                "description": (
                    f"{clean_title.upper()} 😱\n\n"
                    f"{data.get('question', 'Would you attempt this challenge?')}\n"
                    f"Tell us in the comments below! 👇\n\n"
                    f"Transformative reaction analysis and commentary breakdown.\n"
                    f"Credit: Original video by @MrBeast\n\n"
                    f"#MrBeast #Challenge #Shorts #Reaction #Viral #Trending"
                ),
                "tags": ["mrbeast", "mrbeast challenge", "viral", "shorts", "reaction", "extreme challenge"]
            }
    except Exception as e:
        print(f"[Commentary] Puter bridge notice: {e}")
    return None

def generate_commentary_and_script(clip_title):
    clean_title = clean_clip_title(clip_title)
    
    # Try Puter first or Gemini
    puter_res = generate_via_puter(clean_title)
    if puter_res and puter_res.get("narration"):
        return puter_res
        
    prompt = f"""
You are a viral YouTube Shorts creator specializing in MrBeast challenge breakdowns.
Write an energetic 15-20 second commentary script (around 45 to 55 words) analyzing: "{clean_title}".
Return ONLY valid JSON matching this schema:
{{
  "narration": "Full spoken voiceover script text with exciting punctuation",
  "hook_headline": "SHORT UPPERCASE HOOK (Max 28 chars)",
  "title": "VIRAL TITLE (Max 75 chars) #Shorts #MrBeast",
  "question": "Engaging question for comments"
}}
"""
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.85, "response_mime_type": "application/json"}
                },
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                res = json.loads(text)
                return {
                    "narration": res.get("narration"),
                    "hook_headline": res.get("hook_headline", "CAN HE WIN?! 😱"),
                    "title": res.get("title", f"{clean_title.upper()} 😱 #Shorts #MrBeast"),
                    "description": (
                        f"{clean_title.upper()} 😱\n\n"
                        f"{res.get('question', 'Would you attempt this challenge?')}\n"
                        f"Tell us in the comments below! 👇\n\n"
                        f"Transformative reaction analysis and commentary breakdown.\n"
                        f"Credit: Original video by @MrBeast\n\n"
                        f"#MrBeast #Challenge #Shorts #Reaction #Viral #Trending"
                    ),
                    "tags": ["mrbeast", "mrbeast challenge", "viral", "shorts", "reaction", "extreme challenge"]
                }
        except Exception:
            pass

    # High-quality dynamic fallback
    hooks = [
        "CAN HE SURVIVE THIS?! 😱",
        "HE ALMOST LOST IT ALL! 🤯",
        "THE CRAZIEST CHALLENGE EVER! 💸",
        "WOULD YOU RISK $500K? 🤔"
    ]
    chosen_hook = random.choice(hooks)
    narration = (
        f"MrBeast just took challenges to a whole new level! "
        f"In {clean_title}, the stakes were unbelievably high, and one tiny mistake could cost everything! "
        f"Would you have the courage to attempt this? Drop your answer in the comments right now!"
    )
    return {
        "narration": narration,
        "hook_headline": chosen_hook,
        "title": f"HE ALMOST LOST EVERYTHING 😱 | {clean_title[:45]} #Shorts #MrBeast",
        "description": (
            f"{clean_title.upper()} 😱\n\n"
            f"Would you risk it all or play it safe? Drop your answer in the comments below! 👇\n\n"
            f"Transformative reaction analysis and commentary breakdown.\n"
            f"Credit: Original video by @MrBeast\n\n"
            f"#MrBeast #Challenge #Shorts #Reaction #Viral #Trending"
        ),
        "tags": ["mrbeast", "mrbeast challenge", "viral", "shorts", "challenge", "reaction"]
    }

def render_voiceover(narration_text, output_audio_path, output_vtt_path):
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    voice = random.choice(VOICES)
    print(f"[Voiceover] Generating speech with {voice}...")
    
    clean_text = narration_text.replace('"', '').replace("'", "")
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", clean_text,
        "--write-media", output_audio_path,
        "--write-subtitles", output_vtt_path
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(output_audio_path) or os.path.getsize(output_audio_path) < 1000:
        raise RuntimeError(f"Edge-TTS failed: {res.stderr}")
        
    print(f"[Voiceover] Generated audio ({os.path.getsize(output_audio_path)} bytes) & subtitles")
    return output_audio_path, output_vtt_path
