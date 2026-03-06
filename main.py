import os, asyncio, requests, time
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- SETTINGS ---
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpg8n9S4a738h" # Yeh ek achhi Urdu/Hindi voice ID hai

def get_bot_content():
    prompt = "Write a 50-second funny Urdu story about Hulk and his Pakistani Ammi. Format: STORY: [urdu text] SCENES: [6 short English image keywords]"
    url = f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}"
    try:
        r = requests.get(url, timeout=30)
        story = r.text.split("STORY:")[1].split("SCENES:")[0].strip()
        scenes = r.text.split("SCENES:")[1].strip().split(",")
        return story, [s.strip() for s in scenes]
    except:
        return "Hulk ki Ammi ne chappal nikaal li.", ["angry mother", "hulk scared"]

def make_elevenlabs_audio(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open("voice.mp3", "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"ElevenLabs Error: {response.text}")
        return False

def download_images(keywords):
    valid_paths = []
    for i, k in enumerate(keywords[:6]):
        full_p = f"3D Disney style Hulk with a Pakistani mother, {k}"
        url = f"https://image.pollinations.ai/prompt/{full_p.replace(' ', '%20')}?width=720&height=1280&seed={int(time.time())+i}"
        try:
            res = requests.get(url, timeout=20)
            with open(f"img_{i}.jpg", "wb") as f: f.write(res.content)
            valid_paths.append(f"img_{i}.jpg")
        except: continue
    return valid_paths

def create_video(images, audio):
    aud = AudioFileClip(audio)
    duration = aud.duration / len(images)
    clips = [ImageClip(m).set_duration(duration).set_fps(24) for m in images]
    final = concatenate_videoclips(clips, method="compose").set_audio(aud)
    final.write_videofile("hulk_bot_final.mp4", fps=24, codec="libx264")

async def start_bot():
    story, scenes = get_bot_content()
    if make_elevenlabs_audio(story):
        imgs = download_images(scenes)
        create_video(imgs, "voice.mp3")
        print("✅ Success!")

if __name__ == "__main__":
    asyncio.run(start_bot())
