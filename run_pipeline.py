import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from pipeline.beast_fetcher import fetch_viral_candidate, download_video_clip, save_history
from pipeline.commentary_generator import generate_commentary_and_script, render_voiceover
from pipeline.video_editor import render_transformative_short
from pipeline.youtube_uploader import upload_video
from pipeline.facebook_uploader import upload_facebook_reel

def main():
    print("=" * 65)
    print("🎬 24/7 VIRAL MRBEAST TRANSFORMATIVE SHORTS PIPELINE")
    print("=" * 65)
    
    timestamp = int(time.time())
    run_dir = os.path.join("temp", f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # 1. Fetch Viral Candidate
    print("\n[Step 1/5] Selecting Viral MrBeast Highlight...")
    candidate = fetch_viral_candidate()
    raw_clip_path = os.path.join(run_dir, "raw_clip.mp4")
    
    # 2. Download Clip
    download_video_clip(candidate, raw_clip_path)
    
    # 3. Generate Transformative Commentary Script & Metadata
    print("\n[Step 2/5] Generating Original Narration & High-CTR Metadata...")
    meta = generate_commentary_and_script(candidate["title"])
    
    # 4. Generate Voiceover Audio & Synchronized Captions
    print("\n[Step 3/5] Synthesizing Studio Voiceover Narration...")
    voice_audio = os.path.join(run_dir, "voiceover.mp3")
    subtitles_vtt = os.path.join(run_dir, "subtitles.vtt")
    render_voiceover(meta["narration"], voice_audio, subtitles_vtt)
    
    # 5. Render Transformative Vertical Short
    print("\n[Step 4/5] Rendering Transformative 1080x1920 Short...")
    final_output_path = os.path.join("output", f"beast_transformative_{timestamp}.mp4")
    render_transformative_short(
        input_clip=raw_clip_path,
        voiceover_mp3=voice_audio,
        subtitles_vtt=subtitles_vtt,
        hook_headline=meta.get("hook_headline", "INSANE MRBEAST BREAKDOWN 🤯"),
        engagement_text="WOULD YOU DO THIS? 👇",
        output_mp4=final_output_path
    )
    
    # 6. Upload to YouTube
    print("\n[Step 5/6] Uploading Transformative Short to YouTube...")
    video_url = upload_video(
        video_path=final_output_path,
        title=meta["title"],
        description=meta["description"],
        tags=meta["tags"]
    )
    
    # 7. Upload to Facebook Page Reels
    print("\n[Step 6/6] Uploading to Facebook Page Reels...")
    fb_url = upload_facebook_reel(
        video_path=final_output_path,
        description=meta["description"]
    )
    
    # 8. Record History
    save_history(candidate["id"])
    
    print("\n" + "=" * 65)
    print("🎉 VIRAL TRANSFORMATIVE SHORT PUBLISHED SUCCESSFULLY!")
    if video_url:
        print(f"🔗 YouTube Short: {video_url}")
    if fb_url:
        print(f"🔗 Facebook Reel: {fb_url}")
    print("=" * 65)

if __name__ == "__main__":
    main()
