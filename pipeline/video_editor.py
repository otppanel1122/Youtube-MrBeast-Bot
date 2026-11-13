import os
import sys
import re
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(FFMPEG)
if ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

WIDTH = 1080
HEIGHT = 1920

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

def create_overlay_frame(hook_headline, engagement_text, overlay_png):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Top Hook Banner
    banner_title = hook_headline.split("|")[0].split("@")[0].strip().upper()
    if len(banner_title) > 34:
        banner_title = banner_title[:31] + "..."
    if not banner_title or len(banner_title) < 4:
        banner_title = "INSANE MRBEAST BREAKDOWN 🤯"
        
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
    sub_text = engagement_text.upper() if engagement_text else "WOULD YOU DO THIS? 👇"
    s_bbox = draw.textbbox((0, 0), sub_text, font=FONT_SUB)
    sw, sh = s_bbox[2] - s_bbox[0], s_bbox[3] - s_bbox[1]
    
    sx0 = (WIDTH - sw) // 2 - 28
    sy0 = 1440
    sx1 = (WIDTH + sw) // 2 + 28
    sy1 = sy0 + sh + 26
    
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=18, fill=(15, 15, 25, 225), outline=(255, 215, 0, 235), width=3)
    draw.text(((WIDTH - sw) // 2, sy0 + 12), sub_text, font=FONT_SUB, fill=(255, 230, 0), stroke_width=4, stroke_fill=(0, 0, 0))
    
    img.save(overlay_png, "PNG")
    return overlay_png

def vtt_to_ass(vtt_file, ass_file):
    with open(vtt_file, "r", encoding="utf-8") as f:
        content = f.read()

    ass_header = """[Script Info]
Title: MrBeast Viral Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Beast,Arial,66,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,40,40,360,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    pattern = r'(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*\n(.*?)(?=\n\n|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for i, (start, end, text) in enumerate(matches):
        s_ass = start.replace(',', '.')[1:-1]
        e_ass = end.replace(',', '.')[1:-1]
        clean_text = ' '.join(text.strip().split()).upper()
        # Alternate vibrant yellow and crisp white for readability
        color_tag = r'{\c&H00FFFF&}' if i % 2 == 0 else r'{\c&HFFFFFF&}'
        events.append(f'Dialogue: 0,{s_ass},{e_ass},Beast,,0,0,0,,{color_tag}{clean_text}')

    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
    return ass_file

def get_audio_duration(audio_file):
    cmd = [
        FFMPEG, "-i", audio_file
    ]
    p_res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    for line in p_res.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            # HH:MM:SS.xx
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 15.0

def render_transformative_short(input_clip, voiceover_mp3, subtitles_vtt, hook_headline, engagement_text, output_mp4):
    print("[Editor] Starting transformative editing with dynamic subtitles, audio ducking & visual pacing...")
    temp_dir = os.path.dirname(os.path.abspath(output_mp4))
    overlay_png = os.path.join(temp_dir, "overlay.png")
    ass_file = os.path.join(temp_dir, "subtitles.ass")
    
    create_overlay_frame(hook_headline, engagement_text, overlay_png)
    vtt_to_ass(subtitles_vtt, ass_file)
    
    duration = get_audio_duration(voiceover_mp3)
    if duration < 5:
        duration = 15.0
        
    # Resolve absolute paths first before changing directory
    abs_clip = os.path.abspath(input_clip)
    abs_voice = os.path.abspath(voiceover_mp3)
    abs_out = os.path.abspath(output_mp4)

    orig_cwd = os.getcwd()
    os.chdir(temp_dir)
    rel_clip = os.path.relpath(abs_clip, temp_dir)
    rel_voice = os.path.relpath(abs_voice, temp_dir)
    rel_overlay = "overlay.png"
    rel_ass = "subtitles.ass"
    rel_out = os.path.relpath(abs_out, temp_dir)
    
    # Check input dimensions
    cmd_probe = [FFMPEG, "-i", rel_clip]
    p_res = subprocess.run(cmd_probe, stderr=subprocess.PIPE, text=True)
    is_vertical = True
    has_audio = False
    for line in p_res.stderr.splitlines():
        if "Stream #0:" in line and "Audio:" in line:
            has_audio = True
        if "Stream #0:" in line and "Video:" in line and "x" in line:
            parts = line.split("Video:")[1]
            for token in parts.split():
                if "x" in token and token.replace("x", "").isdigit():
                    dims = token.split("x")
                    w, h = int(dims[0]), int(dims[1])
                    if w > h:
                        is_vertical = False
                    break

    progress_filter = f"drawbox=x=0:y=0:w='iw*(t/{duration:.2f})':h=14:color=gold@0.9:t=fill"

    if is_vertical:
        video_filters = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
            f"eq=contrast=1.08:saturation=1.16,{progress_filter}[vbase];"
            f"[vbase][1:v]overlay=0:0[vcomp];"
            f"[vcomp]subtitles={rel_ass}[outv]"
        )
    else:
        video_filters = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,setsar=1[bg];"
            f"[0:v]scale=1080:608:force_original_aspect_ratio=decrease,pad=1080:608:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"eq=contrast=1.08:saturation=1.16[fg];"
            f"[bg][fg]overlay=0:656[vcomp0];"
            f"[vcomp0]{progress_filter}[vcomp1];"
            f"[vcomp1][1:v]overlay=0:0[vcomp2];"
            f"[vcomp2]subtitles={rel_ass}[outv]"
        )

    if has_audio:
        audio_filters = (
            f"[0:a]volume=0.15[bg_a];"
            f"[2:a]volume=1.0[narr_a];"
            f"[bg_a][narr_a]amix=inputs=2:duration=first[out_a]"
        )
    else:
        audio_filters = f"[2:a]volume=1.0[out_a]"

    filter_complex = f"{video_filters};{audio_filters}"

    cmd = [
        FFMPEG, "-y",
        "-i", rel_clip,
        "-i", rel_overlay,
        "-i", rel_voice,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[out_a]",
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.2",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-ar", "44100",
        "-b:a", "192k",
        "-t", f"{duration:.2f}",
        "-movflags", "+faststart",
        rel_out
    ]

    try:
        print("[Editor] Rendering Final Video with FFmpeg...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg render failed: {res.stderr[-500:]}")
            
        print(f"[Editor] Transformative Short Rendered: {output_mp4} ({os.path.getsize(rel_out) / 1024 / 1024:.2f} MB)")
        return output_mp4
    finally:
        os.chdir(orig_cwd)
