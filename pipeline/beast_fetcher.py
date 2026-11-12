import os
import sys
import json
import random
import time
import imageio_ffmpeg
import yt_dlp

# Ensure ffmpeg in PATH
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_exe)
if ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

dst_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
if not os.path.exists(dst_exe) and os.path.exists(ffmpeg_exe):
    try:
        import shutil
        shutil.copyfile(ffmpeg_exe, dst_exe)
    except Exception:
        pass

SOURCES = [
    "https://www.tiktok.com/@mrbeast"
]

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(entry_id):
    hist = load_history()
    hist.append(entry_id)
    if len(hist) > 200:
        hist = hist[-200:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2)
    except Exception:
        pass

def fetch_viral_candidate():
    history = load_history()
    print("[Fetcher] Scanning MrBeast official feeds for viral candidate...")
    
    source_url = random.choice(SOURCES)
    ydl_opts = {
        'extract_flat': True,
        'playlist_items': '1-20',
        'quiet': True
    }
    
    entries = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            res = ydl.extract_info(source_url, download=False)
            entries = res.get('entries', [])
        except Exception as e:
            print(f"[Fetcher] Notice fetching {source_url}: {e}")
            
    # Filter out already clipped entries
    unseen = [e for e in entries if e.get('id') not in history]
    if not unseen:
        unseen = entries
        
    chosen = random.choice(unseen[:10])
    clip_id = chosen.get('id')
    title = chosen.get('title') or "MrBeast Insane Challenge"
    video_url = chosen.get('url') or f"https://www.tiktok.com/@mrbeast/video/{clip_id}"
    
    print(f"[Fetcher] Selected Viral Video: '{title[:60]}' (ID: {clip_id})")
    
    return {
        "id": clip_id,
        "title": title,
        "url": video_url
    }

def download_video_clip(candidate, output_mp4):
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)
    video_url = candidate["url"]
    
    ydl_opts = {
        'outtmpl': output_mp4,
        'merge_output_format': 'mp4',
        'quiet': False
    }
    
    print(f"[Fetcher] Downloading clip from {video_url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        
    if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 100000:
        print(f"[Fetcher] Successfully downloaded clip ({os.path.getsize(output_mp4) / 1024 / 1024:.2f} MB)")
        return output_mp4
        
    base = os.path.splitext(output_mp4)[0]
    for f in os.listdir(os.path.dirname(output_mp4)):
        if f.startswith(os.path.basename(base)) and f.endswith(".mp4"):
            found = os.path.join(os.path.dirname(output_mp4), f)
            print(f"[Fetcher] Located file at {found}")
            return found
            
    raise RuntimeError(f"Failed to download clip {candidate['id']}")
