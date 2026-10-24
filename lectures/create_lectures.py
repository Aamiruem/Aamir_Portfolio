"""Render narrated portfolio lectures from lecture-scripts.md.

Requires edge-tts, Pillow, and imageio-ffmpeg. Narration uses a synthetic
en-IN voice; source photos are read from ../assets/photos.
"""
from __future__ import annotations

import asyncio
import re
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("lecture-scripts.md")
OUT = ROOT / "assets" / "lectures"
VOICE = "en-IN-PrabhatNeural"
SIZE = (1280, 720)
PHOTOS = [ROOT / "assets" / "photos" / f"aamir-work-{i}-hq.webp" for i in (1, 3, 4, 5)]
LESSONS = [
    {"slug": "crop-image-triage", "tag": "AI / ML | COMPUTER VISION"},
    {"slug": "low-stock-alert-api", "tag": "CODING | NODE.JS | EXPRESS"},
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def make_slide(lesson: dict, title: str, narration: str, index: int) -> Path:
    w, h = SIZE
    im = Image.new("RGB", SIZE, "#0b1020")
    d = ImageDraw.Draw(im)
    for x in range(700, w, 42):
        d.line((x, 0, x, h), fill="#121b30", width=1)
    for y in range(0, h, 42):
        d.line((700, y, w, y), fill="#121b30", width=1)
    photo = Image.open(PHOTOS[index % len(PHOTOS)]).convert("RGB")
    photo = ImageOps.fit(photo, (470, 600), centering=(0.5, 0.4))
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 469, 599), radius=22, fill=255)
    im.paste(photo, (50, 60), mask)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((50, 60, 520, 660), radius=22, outline="#53607d", width=2)
    d.text((570, 60), "AAMIR HUSSAIN AZAD", font=font(20, True), fill="#76d5fb")
    d.text((570, 112), lesson["tag"], font=font(17, True), fill="#ffc46a")
    title_font = font(38, True)
    for j, line in enumerate(wrap(d, title, title_font, 630)):
        d.text((570, 172 + j * 49), line, font=title_font, fill="#f2f5ff")
    y = 286
    body_font = font(23)
    for line in wrap(d, narration, body_font, 635)[:8]:
        d.text((572, y), line, font=body_font, fill="#c7d2eb")
        y += 34
    if lesson["slug"] == "crop-image-triage":
        flow = "PHOTO  →  CHECK  →  MODEL  →  REVIEW"
        d.rounded_rectangle((570, 570, 1220, 630), radius=12, fill="#182340", outline="#39708a")
        d.text((590, 587), flow, font=font(18, True), fill="#7de1ff")
    elif "Validate" in title or "Prevent" in title:
        d.rounded_rectangle((570, 570, 1220, 630), radius=12, fill="#182340", outline="#39708a")
        d.text((592, 586), "quantity = 0  ✓     quantity = -1  ✕", font=font(19, True), fill="#7de1ff")
    else:
        d.rounded_rectangle((570, 570, 1220, 630), radius=12, fill="#182340", outline="#39708a")
        d.text((592, 586), "REAL PROBLEM  ·  CLEAR RULES  ·  SAFE FALLBACK", font=font(17, True), fill="#7de1ff")
    d.rectangle((0, h - 8, w, h), fill="#202d50")
    d.rectangle((0, h - 8, int(w * (index + 1) / len(lesson["sections"])), h), fill="#ffb84d")
    path = OUT / f"{lesson['slug']}-scene-{index:02d}.png"
    im.save(path, optimize=True)
    return path


async def make_audio(text: str, path: Path) -> None:
    await edge_tts.Communicate(text, VOICE, rate="-5%", pitch="+0Hz").save(str(path))


def run_ffmpeg(args: list[str]) -> None:
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", *args], check=True)


def seconds_for(audio: Path) -> float:
    probe = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(audio)], capture_output=True, text=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", probe.stderr)
    if not match:
        raise RuntimeError(f"Could not read audio duration: {audio}")
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


def read_production_scripts() -> list[list[tuple[str, str]]]:
    content = SCRIPT.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^## \d+ — )", content, flags=re.MULTILINE)[1:]
    all_sections = []
    for block in blocks:
        narration = block.split("### Narration", 1)[1].split("### On-screen", 1)[0]
        parts = re.split(r"^\*\*([^*]+)\*\*\s*$", narration, flags=re.MULTILINE)
        sections = []
        for i in range(1, len(parts), 2):
            text = " ".join(parts[i + 1].split())
            if text:
                sections.append((parts[i].strip(), text))
        all_sections.append(sections)
    return all_sections


async def render(lesson: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    audio_paths, slides = [], []
    durations = []
    transcript_lines = []
    subtitle_rows = []
    timeline = 0.0
    for i, (heading, narration) in enumerate(lesson["sections"]):
        audio = OUT / f"{lesson['slug']}-scene-{i:02d}.mp3"
        await make_audio(narration, audio)
        audio_paths.append(audio)
        duration = seconds_for(audio)
        durations.append(duration)
        transcript_lines.append(f"## {heading}\n\n{narration}\n")
        words = narration.split()
        groups = [words[j:j + 10] for j in range(0, len(words), 10)]
        total_words = max(len(words), 1)
        consumed = 0
        for group in groups:
            start = timeline + duration * consumed / total_words
            consumed += len(group)
            end = timeline + duration * consumed / total_words
            subtitle_rows.append((start, end, " ".join(group)))
        timeline += duration
        excerpt = narration.split(". ")[0].strip()
        slides.append(make_slide(lesson, heading, excerpt + ("." if not excerpt.endswith(".") else ""), i))
    (OUT / f"{lesson['slug']}-transcript.md").write_text("\n".join(transcript_lines), encoding="utf-8")

    def timestamp(value: float) -> str:
        millis = round(value * 1000)
        hours, millis = divmod(millis, 3_600_000)
        minutes, millis = divmod(millis, 60_000)
        secs, millis = divmod(millis, 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    srt = "\n\n".join(f"{i}\n{timestamp(start)} --> {timestamp(end)}\n{text}" for i, (start, end, text) in enumerate(subtitle_rows, 1))
    (OUT / f"{lesson['slug']}-captions.srt").write_text(srt + "\n", encoding="utf-8")
    audio_list = OUT / f"{lesson['slug']}-audio.txt"
    audio_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in audio_paths), encoding="utf-8")
    full_audio = OUT / f"{lesson['slug']}-narration.mp3"
    run_ffmpeg(["-y", "-f", "concat", "-safe", "0", "-i", str(audio_list), "-c:a", "libmp3lame", "-q:a", "3", str(full_audio)])
    # A matching still card accompanies each narrated section; ffmpeg creates a
    # variable-frame-rate slideshow and muxes the full generated narration.
    slide_list = OUT / f"{lesson['slug']}-slides.txt"
    lines = []
    for image, duration in zip(slides, durations):
        lines.extend([f"file '{image.as_posix()}'", f"duration {duration:.3f}"])
    lines.append(f"file '{slides[-1].as_posix()}'")
    slide_list.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output = OUT / f"{lesson['slug']}.mp4"
    run_ffmpeg(["-y", "-f", "concat", "-safe", "0", "-i", str(slide_list), "-i", str(full_audio), "-vf", "fps=15,scale=960:540,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-c:a", "aac", "-b:a", "112k", "-shortest", "-movflags", "+faststart", str(output)])
    print(f"Created: {output.relative_to(ROOT)}")
    print(f"Narration: {full_audio.relative_to(ROOT)}")


async def main() -> None:
    scripts = read_production_scripts()
    for lesson, sections in zip(LESSONS, scripts):
        lesson["sections"] = sections
        await render(lesson)


if __name__ == "__main__":
    asyncio.run(main())
