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

FONT_BANNER = get_font(52)
FONT_SUB = get_font(42)

def create_overlay_frame(title, hook_text, overlay_png):
    """
    Creates high-impact top and bottom graphics overlays in 1080x1920 transparent PNG.
    """
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Top Hook Banner
    # Truncate and clean title
    banner_title = title.split("|")[0].strip().upper()
    if len(banner_title) > 36:
        banner_title = banner_title[:33] + "..."
        
    bbox = draw.textbbox((0, 0), banner_title, font=FONT_BANNER)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    bx0 = (WIDTH - bw) // 2 - 36
    by0 = 240
    bx1 = (WIDTH + bw) // 2 + 36
    by1 = by0 + bh + 32
    
    # Glowing yellow/red gradient-like badge
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=20, fill=(235, 30, 45, 230), outline=(255, 255, 255, 240), width=4)
    draw.text(((WIDTH - bw) // 2, by0 + 14), banner_title, font=FONT_BANNER, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    
    # 2. Bottom Engagement Badge
    sub_text = hook_text.upper() if hook_text else "WAIT FOR THE END! 😱"
    s_bbox = draw.textbbox((0, 0), sub_text, font=FONT_SUB)
    sw, sh = s_bbox[2] - s_bbox[0], s_bbox[3] - s_bbox[1]
    
    sx0 = (WIDTH - sw) // 2 - 32
    sy0 = 1380
    sx1 = (WIDTH + sw) // 2 + 32
    sy1 = sy0 + sh + 28
    
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=18, fill=(15, 15, 20, 220), outline=(255, 215, 0, 230), width=3)
    draw.text(((WIDTH - sw) // 2, sy0 + 12), sub_text, font=FONT_SUB, fill=(255, 230, 0), stroke_width=4, stroke_fill=(0, 0, 0))
    
    img.save(overlay_png, "PNG")
    return overlay_png

def render_mrbeast_short(input_clip, title, hook_text, output_mp4):
    """
    Renders 1080x1920 vertical Short with:
    - Blurred background video
    - Crisp centered 16:9 foreground
    - High-CTR graphical overlays
    - Faststart MOOV atom compliance
    """
    print("[Editor] Packaging clip into viral 9:16 Short...")
    temp_dir = os.path.dirname(output_mp4)
    overlay_png = os.path.join(temp_dir, "overlay.png")
    create_overlay_frame(title, hook_text, overlay_png)
    
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,setsar=1[bg];"
        "[0:v]scale=1080:608:force_original_aspect_ratio=decrease,pad=1080:608:(ow-iw)/2:(oh-ih)/2,setsar=1[fg];"
        "[bg][fg]overlay=0:656[comp];"
        "[comp][1:v]overlay=0:0[v]"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-i", input_clip,
        "-i", overlay_png,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "0:a",
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
