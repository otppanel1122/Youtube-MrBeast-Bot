import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def upload_facebook_reel(video_path, description, page_id=None, page_access_token=None):
    if not page_id:
        page_id = os.getenv("FACEBOOK_PAGE_ID")
    if not page_access_token:
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        
    if not (page_id and page_access_token):
        print("[Facebook] Notice: FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN not yet configured. Skipping Facebook upload.")
        return None
        
    print(f"[Facebook] Initializing Facebook Reel upload on Page ID: {page_id}...")
    
    # Step 1: Initialize Reel upload session
    start_url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    try:
        init_res = requests.post(start_url, json={
            "upload_phase": "start",
            "access_token": page_access_token
        }, timeout=30)
        
        if init_res.status_code != 200:
            print(f"[Facebook] Init failed ({init_res.status_code}): {init_res.text}")
            return None
            
        video_id = init_res.json().get("video_id")
        print(f"[Facebook] Reel session initialized. Video ID: {video_id}")
        
        # Step 2: Upload Video File Binary
        upload_url = f"https://rupload.facebook.com/video-upload/v20.0/{video_id}"
        file_size = os.path.getsize(video_path)
        
        headers = {
            "Authorization": f"OAuth {page_access_token}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        
        print(f"[Facebook] Uploading Reel video file ({file_size / 1024 / 1024:.2f} MB)...")
        with open(video_path, "rb") as f:
            up_res = requests.post(upload_url, headers=headers, data=f, timeout=180)
            
        if up_res.status_code not in (200, 201):
            print(f"[Facebook] Binary upload failed ({up_res.status_code}): {up_res.text}")
            return None
            
        print("[Facebook] Video file binary uploaded. Publishing Reel...")
        
        # Step 3: Finish & Publish Reel
        finish_res = requests.post(start_url, json={
            "upload_phase": "finish",
            "access_token": page_access_token,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": description[:2000]
        }, timeout=30)
        
        if finish_res.status_code == 200:
            fb_url = f"https://www.facebook.com/reel/{video_id}"
            print(f"[Facebook] 🎉 FACEBOOK REEL PUBLISHED: {fb_url}")
            return fb_url
        else:
            print(f"[Facebook] Publish failed ({finish_res.status_code}): {finish_res.text}")
            return None
    except Exception as e:
        print(f"[Facebook] Error during Facebook Reels upload: {e}")
        return None
