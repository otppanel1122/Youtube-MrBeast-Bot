import os
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
WIDTH = 1080
HEIGHT = 1920
FPS = 30

def get_font(size=52):
    candidates = [
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

FONT_BANNER = get_font(50)
FONT_SUB = get_font(40)

def create_overlay_frame(title, hook_text, overlay_png):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Top Hook Banner
    banner_title = title.split("|")[0].split("@")[0].strip().upper()
    if len(banner_title) > 34:
        banner_title = banner_title[:31] + "..."
    if not banner_title or len(banner_title) < 4:
        banner_title = "INSANE MRBEAST CHALLENGE"
        
    bbox = draw.textbbox((0, 0), banner_title, font=FONT_BANNER)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    bx0 = (WIDTH - bw) // 2 - 32
    by0 = 220
    bx1 = (WIDTH + bw) // 2 + 32
    by1 = by0 + bh + 30
    
    # High-impact red/gold badge with white border
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=20, fill=(230, 25, 45, 235), outline=(255, 255, 255, 240), width=4)
    draw.text(((WIDTH - bw) // 2, by0 + 13), banner_title, font=FONT_BANNER, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    
    # 2. Bottom Engagement Badge
    sub_text = hook_text.upper() if hook_text else "WAIT FOR THE END! 😱"
    s_bbox = draw.textbbox((0, 0), sub_text, font=FONT_SUB)
    sw, sh = s_bbox[2] - s_bbox[0], s_bbox[3] - s_bbox[1]
    
    sx0 = (WIDTH - sw) // 2 - 28
    sy0 = 1420
    sx1 = (WIDTH + sw) // 2 + 28
    sy1 = sy0 + sh + 26
    
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=18, fill=(15, 15, 25, 220), outline=(255, 215, 0, 235), width=3)
    draw.text(((WIDTH - sw) // 2, sy0 + 12), sub_text, font=FONT_SUB, fill=(255, 230, 0), stroke_width=4, stroke_fill=(0, 0, 0))
    
    img.save(overlay_png, "PNG")
    return overlay_png

def render_mrbeast_short(input_clip, title, hook_text, output_mp4):
    print("[Editor] Packaging clip into viral 9:16 Short...")
    temp_dir = os.path.dirname(output_mp4)
    overlay_png = os.path.join(temp_dir, "overlay.png")
    create_overlay_frame(title, hook_text, overlay_png)
    
    # Check input dimensions
    cmd_probe = [
        FFMPEG, "-i", input_clip
    ]
    p_res = subprocess.run(cmd_probe, stderr=subprocess.PIPE, text=True)
    is_vertical = True
    for line in p_res.stderr.splitlines():
        if "Stream #0:0" in line and "Video:" in line and "x" in line:
            parts = line.split("Video:")[1]
            for token in parts.split():
                if "x" in token and token.replace("x", "").isdigit():
                    dims = token.split("x")
                    w, h = int(dims[0]), int(dims[1])
                    if w > h:
                        is_vertical = False
                    break
            break
            
    if is_vertical:
        # Scale to 1080x1920
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v];"
            "[v][1:v]overlay=0:0[outv]"
        )
    else:
        # Blurred background + centered 16:9
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,setsar=1[bg];"
            "[0:v]scale=1080:608:force_original_aspect_ratio=decrease,pad=1080:608:(ow-iw)/2:(oh-ih)/2,setsar=1[fg];"
            "[bg][fg]overlay=0:656[comp];"
            "[comp][1:v]overlay=0:0[outv]"
        )
        
    cmd = [
        FFMPEG, "-y",
        "-i", input_clip,
        "-i", overlay_png,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.2",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-ar", "44100",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        output_mp4
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed: {res.stderr[-400:]}")
        
    print(f"[Editor] Successfully rendered viral Short: {output_mp4} ({os.path.getsize(output_mp4) / 1024 / 1024:.2f} MB)")
    return output_mp4
