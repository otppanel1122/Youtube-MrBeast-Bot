import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from pipeline.beast_fetcher import fetch_viral_candidate, download_video_clip, save_history
from pipeline.metadata_generator import generate_metadata
from pipeline.video_editor import render_mrbeast_short
from pipeline.youtube_uploader import upload_video

def main():
    print("=" * 65)
    print("🎬 24/7 VIRAL MRBEAST SHORTS AUTOMATION PIPELINE")
    print("=" * 65)
    
    timestamp = int(time.time())
    run_dir = os.path.join("temp", f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # 1. Fetch Viral Candidate
    print("\n[Step 1/4] Scanning & Selecting Viral MrBeast Highlight...")
    candidate = fetch_viral_candidate()
    raw_clip_path = os.path.join(run_dir, "raw_clip.mp4")
    
    # 2. Download Clip
    download_video_clip(candidate, raw_clip_path)
    
    # 3. Generate Metadata & Hooks
    print("\n[Step 2/4] Generating High-CTR Viral Metadata...")
    meta = generate_metadata(candidate["title"], candidate["segment_name"])
    
    # 4. Package 9:16 Vertical Short
    print("\n[Step 3/4] Rendering 1080x1920 Vertical Short...")
    final_output_path = os.path.join("output", f"beast_short_{timestamp}.mp4")
    render_mrbeast_short(
        input_clip=raw_clip_path,
        title=meta.get("title", candidate["title"]),
        hook_text=meta.get("hook", "WAIT TILL THE END! 😱"),
        output_mp4=final_output_path
    )
    
    # 5. Upload to YouTube
    print("\n[Step 4/4] Uploading to YouTube Shorts...")
    video_url = upload_video(
        video_path=final_output_path,
        title=meta["title"],
        description=meta["description"],
        tags=meta["tags"]
    )
    
    # 6. Save history to avoid duplicate segments
    history_key = f"{candidate['id']}_{candidate['segment_name']}"
    save_history(history_key)
    
    print("\n" + "=" * 65)
    print(f"🎉 MRBEAST SHORT PUBLISHED SUCCESSFULLY!")
    if video_url:
        print(f"🔗 Video URL: {video_url}")
    print("=" * 65)

if __name__ == "__main__":
    main()
