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

FALLBACK_VIRAL_CLIPS = [
    {"id": "7707342481465036062", "title": "Go support Juan and check out JuanStopShop.com today! @Shopify", "url": "https://www.tiktok.com/@mrbeast/video/7707342481465036062"},
    {"id": "7705603633437527327", "title": "Who will win Tareq", "url": "https://www.tiktok.com/@mrbeast/video/7705603633437527327"},
    {"id": "7703595535009156383", "title": "Bro really juan that challenge", "url": "https://www.tiktok.com/@mrbeast/video/7703595535009156383"},
    {"id": "7703204609497550110", "title": "Caitlin Clark do i have a shot in the NBA?", "url": "https://www.tiktok.com/@mrbeast/video/7703204609497550110"},
    {"id": "7702441498515688734", "title": "Did we win halloween", "url": "https://www.tiktok.com/@mrbeast/video/7702441498515688734"},
    {"id": "7700729659301924126", "title": "My face actually feels great!", "url": "https://www.tiktok.com/@mrbeast/video/7700729659301924126"},
    {"id": "7698794225453813022", "title": "Don't be like Nolan and go play modernwarfare4 today!", "url": "https://www.tiktok.com/@mrbeast/video/7698794225453813022"},
    {"id": "7698435898240683295", "title": "The breakfast of champions", "url": "https://www.tiktok.com/@mrbeast/video/7698435898240683295"},
    {"id": "7698087411321949471", "title": "Guess who is the olympic medalist?", "url": "https://www.tiktok.com/@mrbeast/video/7698087411321949471"},
    {"id": "7697653789007908126", "title": "It really be like that", "url": "https://www.tiktok.com/@mrbeast/video/7697653789007908126"},
    {"id": "7694374092127898911", "title": "Bro stands no chance MrBeast Lab Mega Mutators", "url": "https://www.tiktok.com/@mrbeast/video/7694374092127898911"},
    {"id": "7693297157662592287", "title": "Bro is so natural at aura farming", "url": "https://www.tiktok.com/@mrbeast/video/7693297157662592287"},
    {"id": "7692976442463866142", "title": "wifey", "url": "https://www.tiktok.com/@mrbeast/video/7692976442463866142"},
    {"id": "7689501576511245598", "title": "guys don't laugh Erling Haaland", "url": "https://www.tiktok.com/@mrbeast/video/7689501576511245598"},
    {"id": "7689134313044184351", "title": "Messing around in the MrBeast Lab", "url": "https://www.tiktok.com/@mrbeast/video/7689134313044184351"},
    {"id": "7687696606044376350", "title": "scariest meal of my life Erling Haaland", "url": "https://www.tiktok.com/@mrbeast/video/7687696606044376350"},
    {"id": "7686940133609786655", "title": "we nailed it Erling Haaland", "url": "https://www.tiktok.com/@mrbeast/video/7686940133609786655"},
    {"id": "7683649763480309022", "title": "I am so unpredictable", "url": "https://www.tiktok.com/@mrbeast/video/7683649763480309022"},
    {"id": "7683332577364643103", "title": "I have never seen a class so eager to read", "url": "https://www.tiktok.com/@mrbeast/video/7683332577364643103"},
    {"id": "7682108829424700702", "title": "All in a days work", "url": "https://www.tiktok.com/@mrbeast/video/7682108829424700702"},
    {"id": "7681056640212258078", "title": "subscribe for a cookie", "url": "https://www.tiktok.com/@mrbeast/video/7681056640212258078"},
    {"id": "7680982718900981022", "title": "gave a quarter back to my hood call me tom brady", "url": "https://www.tiktok.com/@mrbeast/video/7680982718900981022"},
    {"id": "7680231103294197022", "title": "we really cooked this up", "url": "https://www.tiktok.com/@mrbeast/video/7680231103294197022"},
    {"id": "7679839713573784863", "title": "Should hood mr beast drop an album", "url": "https://www.tiktok.com/@mrbeast/video/7679839713573784863"},
    {"id": "7677375185028271391", "title": "would you take the car or nah?", "url": "https://www.tiktok.com/@mrbeast/video/7677375185028271391"},
    {"id": "7673587109537615135", "title": "it was my best video ever", "url": "https://www.tiktok.com/@mrbeast/video/7673587109537615135"},
    {"id": "7672078693803609374", "title": "This is why you should never skip school", "url": "https://www.tiktok.com/@mrbeast/video/7672078693803609374"},
    {"id": "7671696914542300447", "title": "My team said i should wear this fit to the met gala", "url": "https://www.tiktok.com/@mrbeast/video/7671696914542300447"},
    {"id": "7670566355153833246", "title": "The last one was hard", "url": "https://www.tiktok.com/@mrbeast/video/7670566355153833246"},
    {"id": "7670199761282075935", "title": "I am as real as they come", "url": "https://www.tiktok.com/@mrbeast/video/7670199761282075935"},
    {"id": "7669561168653978910", "title": "Btw this dance took me hours to learn", "url": "https://www.tiktok.com/@mrbeast/video/7669561168653978910"},
    {"id": "7665011704031399198", "title": "Surprising my girlfriend", "url": "https://www.tiktok.com/@mrbeast/video/7665011704031399198"},
    {"id": "7663636840288668959", "title": "James Patterson and I wrote a book!", "url": "https://www.tiktok.com/@mrbeast/video/7663636840288668959"},
    {"id": "7661646236516093215", "title": "Why did we do this to ourselves", "url": "https://www.tiktok.com/@mrbeast/video/7661646236516093215"},
    {"id": "7659558620098465055", "title": "Check your DMs surprise", "url": "https://www.tiktok.com/@mrbeast/video/7659558620098465055"},
    {"id": "7654638524729216287", "title": "I raced Usain Bolt", "url": "https://www.tiktok.com/@mrbeast/video/7654638524729216287"},
    {"id": "7651447222449556767", "title": "At least he got the last one", "url": "https://www.tiktok.com/@mrbeast/video/7651447222449556767"},
    {"id": "7650364966352014623", "title": "Tag who you see in the comments! You wont want to miss this", "url": "https://www.tiktok.com/@mrbeast/video/7650364966352014623"},
    {"id": "7642346910266739999", "title": "Thanks for the help boys", "url": "https://www.tiktok.com/@mrbeast/video/7642346910266739999"},
    {"id": "7634583942254972190", "title": "We are just one big happy family", "url": "https://www.tiktok.com/@mrbeast/video/7634583942254972190"}
]

HISTORY_FILE = "history.json"

def get_ydl_instance(extra_cli_args=None, base_opts=None):
    cli_args = ['--impersonate', 'Chrome-131']
    if extra_cli_args:
        cli_args.extend(extra_cli_args)
    try:
        parsed = yt_dlp.parse_options(cli_args)
        opts = dict(parsed[3])
        if base_opts:
            opts.update(base_opts)
        return yt_dlp.YoutubeDL(opts)
    except Exception as e:
        print(f"[Fetcher] Impersonate setup note: {e}, using default options")
        return yt_dlp.YoutubeDL(base_opts or {})

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
    hist.append(str(entry_id))
    if len(hist) > 200:
        hist = hist[-200:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2)
    except Exception:
        pass

def fetch_viral_candidate():
    history = [str(x) for x in load_history()]
    print("[Fetcher] Scanning MrBeast official feeds for viral candidate...")
    
    entries = []
    source_url = random.choice(SOURCES)
    
    try:
        ydl = get_ydl_instance(base_opts={'extract_flat': True, 'playlist_items': '1-25', 'quiet': True})
        with ydl:
            res = ydl.extract_info(source_url, download=False)
            raw_entries = res.get('entries', []) if res else []
            for e in raw_entries:
                if e and e.get('id'):
                    entries.append({
                        "id": str(e.get('id')),
                        "title": e.get('title') or "MrBeast Insane Viral Challenge",
                        "url": e.get('url') or f"https://www.tiktok.com/@mrbeast/video/{e.get('id')}"
                    })
    except Exception as e:
        print(f"[Fetcher] Notice fetching live profile: {e}")
        
    # If live extraction had zero entries (e.g. data center IP block on profile page), use curated pool
    if not entries:
        print("[Fetcher] Live profile feed unavailable or empty; activating curated viral MrBeast pool.")
        entries = list(FALLBACK_VIRAL_CLIPS)
        
    # Filter out already clipped entries
    unseen = [e for e in entries if str(e.get('id')) not in history]
    if not unseen:
        print("[Fetcher] All candidates in current pool were previously used; recycling unseen from fallback.")
        unseen = [e for e in FALLBACK_VIRAL_CLIPS if str(e.get('id')) not in history]
        if not unseen:
            unseen = entries
            
    chosen = random.choice(unseen)
    clip_id = str(chosen.get('id'))
    title = chosen.get('title') or "MrBeast Insane Viral Challenge"
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
    
    base_opts = {
        'outtmpl': output_mp4,
        'merge_output_format': 'mp4',
        'quiet': False
    }
    
    print(f"[Fetcher] Downloading clip from {video_url}...")
    try:
        ydl = get_ydl_instance(base_opts=base_opts)
        with ydl:
            ydl.download([video_url])
    except Exception as e:
        print(f"[Fetcher] Download error on primary URL: {e}")
        # Try alternate fallback clip
        for fb in FALLBACK_VIRAL_CLIPS:
            if fb["id"] != candidate["id"]:
                print(f"[Fetcher] Attempting fallback clip: {fb['url']}")
                try:
                    ydl_fb = get_ydl_instance(base_opts=base_opts)
                    with ydl_fb:
                        ydl_fb.download([fb["url"]])
                    candidate["id"] = fb["id"]
                    candidate["title"] = fb["title"]
                    candidate["url"] = fb["url"]
                    break
                except Exception:
                    continue
        
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
