import os
import requests
import io
import time
from PIL import Image
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

# Configuration
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
# 'Josh' ki standard ID jo har account mein hoti hai
VOICE_ID = "TxGEqnSAs9dnFT47v3tM" 
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_VIDEO = "hulk_bot_final.mp4"

def fetch_content():
    # Urdu script for Pakistani Ammi theme
    prompt = "Write a 40-second funny Urdu story about Hulk and his strict Pakistani mother. Use ### as a separator for 5 image keywords at the end."
    url = f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}"
    try:
        response = requests.get(url, timeout=30)
        content = response.text
        if "###" in content:
            story, k_part = content.split("###", 1)
            keywords = [k.strip() for k in k_part.split(",")[:5]]
        else:
            story = content
            keywords = ["Hulk", "Pakistani Mother", "Funny Scene", "Kitchen", "Angry"]
        return story, keywords
    except:
        return "Hulk ki Ammi ne chappal dikhayi.", ["angry mom", "hulk scared"]

def generate_audio(text):
    # Endpoint URL ko correct format mein rakha hai taaki 404 na aaye
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": MODEL_ID}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open("voice.mp3", "wb") as f:
            f.write(response.content)
        return "voice.mp3"
    else:
        print(f"ElevenLabs Error: {response.text}")
        return None

def process_images(keywords):
    paths = []
    for i, k in enumerate(keywords):
        img_url = f"https://image.pollinations.ai/prompt/3D%20Hulk%20with%20Pakistani%20Ammi%20{k.replace(' ', '%20')}?width=720&height=1280&seed={int(time.time())+i}"
        try:
            r = requests.get(img_url, timeout=20)
            # Re-saving with Pillow to avoid 'avcodec_send_packet'
            img = Image.open(io.BytesIO(r.content)).convert('RGB')
            p = f"fixed_{i}.jpg"
            img.save(p, 'JPEG')
            paths.append(p)
        except: continue
    return paths

def create_video(audio_p, image_ps):
    audio = AudioFileClip(audio_p)
    duration = audio.duration / len(image_ps)
    clips = [ImageClip(p).set_duration(duration).set_fps(24) for p in image_ps]
    # Concatenate clips sequentially
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile(OUTPUT_VIDEO, codec='libx264', audio_codec='aac', fps=24)

if __name__ == "__main__":
    if not ELEVENLABS_KEY:
        print("❌ Error: API Key missing.")
    else:
        s, k = fetch_content()
        a_path = generate_audio(s)
        if a_path:
            i_paths = process_images(k)
            if i_paths:
                create_video(a_path, i_paths)
                print("🚀 Video Success!")
