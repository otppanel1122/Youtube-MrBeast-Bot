import os
import sys
import json
import random
import time
import imageio_ffmpeg
import yt_dlp

# Ensure ffmpeg is in PATH
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

CHANNELS = [
    "https://www.youtube.com/@MrBeast/videos",
    "https://www.youtube.com/@MrBeastGaming/videos",
    "https://www.youtube.com/@MrBeast2/videos"
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
    if len(hist) > 100:
        hist = hist[-100:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2)
    except Exception:
        pass

def fetch_viral_candidate():
    history = load_history()
    print("[Fetcher] Scanning MrBeast channels for viral candidate...")
    
    channel_url = random.choice(CHANNELS)
    ydl_opts = {
        'extract_flat': True,
        'playlist_items': '1-10',
        'extractor_args': {'youtube': {'player_client': ['android']}},
        'quiet': True
    }
    
    entries = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            res = ydl.extract_info(channel_url, download=False)
            entries = res.get('entries', [])
        except Exception as e:
            print(f"[Fetcher] Channel fetch notice: {e}")
            
    if not entries:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info("https://www.youtube.com/@MrBeast/videos", download=False)
            entries = res.get('entries', [])
            
    candidates = []
    for e in entries:
        duration = e.get('duration') or 600
        if duration >= 90:
            candidates.append(e)
            
    if not candidates:
        candidates = entries
        
    chosen = random.choice(candidates[:6])
    vid_id = chosen.get('id')
    title = chosen.get('title') or "Insane MrBeast Challenge"
    duration = chosen.get('duration') or 900
    video_url = f"https://www.youtube.com/watch?v={vid_id}"
    
    print(f"[Fetcher] Selected Video: '{title}' ({duration}s)")
    
    clip_options = [
        {"name": "Hook", "start": 8, "end": 42},
        {"name": "Climax", "start": max(30, int(duration - 75)), "end": max(65, int(duration - 38))},
        {"name": "Challenge Twist", "start": int(duration * 0.45), "end": int(duration * 0.45) + 35}
    ]
    
    chosen_segment = None
    for opt in clip_options:
        seg_key = f"{vid_id}_{opt['name']}"
        if seg_key not in history:
            chosen_segment = opt
            break
            
    if not chosen_segment:
        chosen_segment = random.choice(clip_options)
        
    start_sec = chosen_segment["start"]
    end_sec = chosen_segment["end"]
    clip_len = end_sec - start_sec
    print(f"[Fetcher] Selected {chosen_segment['name']} Segment: {start_sec}s -> {end_sec}s ({clip_len}s long)")
    
    return {
        "id": vid_id,
        "segment_name": chosen_segment["name"],
        "title": title,
        "url": video_url,
        "start": start_sec,
        "end": end_sec,
        "duration": duration
    }

def download_video_clip(candidate, output_mp4):
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)
    start_time = candidate["start"]
    end_time = candidate["end"]
    
    def download_range_func(info_dict, ydl):
        return [{'start_time': start_time, 'end_time': end_time, 'title': 'viral_segment'}]

    # Try android client first (bypasses YouTube datacenter bot checks)
    clients_to_try = [
        ['android'],
        ['android_vr'],
        ['mweb']
    ]
    
    for client in clients_to_try:
        ydl_opts = {
            'format': '18/best[height<=720]/best',
            'download_ranges': download_range_func,
            'outtmpl': output_mp4,
            'merge_output_format': 'mp4',
            'force_keyframes_at_cuts': True,
            'extractor_args': {'youtube': {'player_client': client}},
            'quiet': False
        }
        
        try:
            print(f"[Fetcher] Attempting download via client '{client[0]}'...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([candidate["url"]])
                
            if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 100000:
                print(f"[Fetcher] Successfully downloaded clip to {output_mp4} ({os.path.getsize(output_mp4) / 1024 / 1024:.2f} MB)")
                return output_mp4
        except Exception as e:
            print(f"[Fetcher] Client '{client[0]}' notice: {e}")
            
    # Check if file was saved with alternative name
    base = os.path.splitext(output_mp4)[0]
    for f in os.listdir(os.path.dirname(output_mp4)):
        if f.startswith(os.path.basename(base)) and f.endswith(".mp4"):
            found = os.path.join(os.path.dirname(output_mp4), f)
            print(f"[Fetcher] Located downloaded file at {found}")
            return found
            
    raise RuntimeError(f"Failed to download clip for {candidate['id']}")
