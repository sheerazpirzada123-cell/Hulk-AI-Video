"""
Hulk AI Video Generator (single-file version)

What it does:
1) Uses Gemini to generate a Hindi story + 12 scene prompts (English)
2) Uses edge-tts to generate voiceover MP3 for the story
3) Downloads 12 images from pollinations.ai using the prompts
4) Builds a vertical video (1080x1920) with crossfades, synced to audio

Requirements:
  pip install google-generativeai edge-tts moviepy requests

System dependency:
  ffmpeg must be installed and available on PATH

Environment:
  GEMINI_API_KEY must be set
Optional:
  GEMINI_MODEL (default: gemini-1.5-flash)
"""

from __future__ import annotations

import os
import re
import json
import shutil
import asyncio
from pathlib import Path
from urllib.parse import quote

import requests
import edge_tts
import google.generativeai as genai

# MoviePy imports (compatible with common installs)
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError as e:
    raise ImportError(
        "moviepy import failed. Install with: pip install moviepy"
    ) from e


# ----------------------------
# Configuration
# ----------------------------
OUTPUT_DIR = Path("out")
OUTPUT_DIR.mkdir(exist_ok=True)

VOICE_NAME = os.getenv("EDGE_TTS_VOICE", "hi-IN-MadhurNeural")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

IMAGE_W = int(os.getenv("IMAGE_W", "1080"))
IMAGE_H = int(os.getenv("IMAGE_H", "1920"))
NUM_SCENES = int(os.getenv("NUM_SCENES", "12"))

# Crossfade duration between images (seconds)
FADE_SEC = float(os.getenv("FADE_SEC", "0.5"))

# Timeouts
IMAGE_TIMEOUT_SEC = float(os.getenv("IMAGE_TIMEOUT_SEC", "60"))
GEMINI_TIMEOUT_NOTE = "Gemini timeout handling depends on upstream; retry manually if needed."


# ----------------------------
# Utilities / Validation
# ----------------------------
def require_env():
    if not GEMINI_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set (export/set it and rerun).")


def require_ffmpeg():
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found on PATH. Install ffmpeg and make sure it's available in your terminal."
        )


def safe_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


# ----------------------------
# Gemini content generation
# ----------------------------
def build_prompt() -> str:
    # Stronger instructions + strict format to reduce parsing failures
    return f"""
You are writing content for a short vertical video.

Return ONLY in the following format (no extra text, no markdown):

STORY:
<Hindi story, funny, about 90 seconds when read aloud>

SCENES:
<Exactly {NUM_SCENES} English image prompts, separated by commas. Each prompt should be vivid, cinematic, and safe-for-work.>

Topic: Hulk and his Indian Mom.
""".strip()


def parse_gemini_output(text: str) -> tuple[str, list[str]]:
    """
    Parses:
      STORY:
      ...
      SCENES:
      prompt1, prompt2, ...
    """
    if not text or "STORY" not in text or "SCENES" not in text:
        raise RuntimeError(f"Unexpected Gemini output (missing markers):\n{text}")

    # Regex to be more resilient to spacing/newlines
    m = re.search(r"STORY\s*:\s*(.*?)\s*SCENES\s*:\s*(.*)$", text, flags=re.S | re.I)
    if not m:
        raise RuntimeError(f"Could not parse Gemini output:\n{text}")

    story = m.group(1).strip()
    scenes_raw = m.group(2).strip()

    prompts = [p.strip() for p in scenes_raw.split(",") if p.strip()]
    if len(prompts) < NUM
