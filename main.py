import os
import requests
import io
import time
from PIL import Image
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "TxGEqnSAs9dnFT47v3tM" # Josh - Standard Voice
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_VIDEO = "hulk_bot_final.mp4"

def fetch_content():
    prompt = "Write a funny 40-second Urdu story about Hulk and a strict Pakistani mother. Provide 5 image keywords at the end separated by ###."
    try:
        response = requests.get(f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}", timeout=30)
        content = response.text
        if "###" in content:
            story, k_part = content.split("###", 1)
            keywords = [k.strip() for k in k_part.split(",")[:5]]
        else:
            story, keywords = content, ["Hulk scared", "Pakistani kitchen", "Ammi with chappal", "Hulk eating", "Funny face"]
        return story, keywords
    except:
        return "Hulk ki Ammi ne use chappal dikhayi.", ["angry mom", "hulk scared"]

def generate_audio(story):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    data = {"text": story, "model_id": MODEL_ID}
    res = requests.post(url, json=data, headers=headers)
    res.raise_for_status()
    with open("temp_audio.mp3", "wb") as f:
        f.write(res.content)
    return "temp_audio.mp3"

def process_images(keywords):
    paths = []
    for i, k in enumerate(keywords):
        url = f"https://image.pollinations.ai/prompt/3D%20Disney%20Hulk%20Pakistani%20{k.replace(' ', '%20')}?width=720&height=1280&seed={int(time.time())+i}"
        try:
            r = requests.get(url, timeout=20)
            img = Image.open(io.BytesIO(r.content)).convert('RGB')
            p = f"fixed_{i}.jpg"
            img.save(p, 'JPEG')
            paths.append(p)
        except: continue
    return paths

def create_video(audio_p, image_ps):
    aud = AudioFileClip(audio_p)
    dur = aud.duration / len(image_ps)
    # Concatenate use karein taaki images line se chalein
    clips = [ImageClip(p).set_duration(dur).set_fps(24) for p in image_ps]
    final = concatenate_videoclips(clips, method="compose").set_audio(aud)
    final.write_videofile(OUTPUT_VIDEO, codec='libx264', audio_codec='aac', fps=24)

if __name__ == "__main__":
    s, k = fetch_content()
    a_path = generate_audio(s)
    i_paths = process_images(k)
    create_video(a_path, i_paths)
    print("✅ Done!")
