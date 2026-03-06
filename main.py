import os, asyncio, requests, time
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- SETTINGS ---
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
# 'Josh' voice ID jo har account mein by default hoti hai
VOICE_ID = "TxGEqnSAs9dnFT47v3tM" 

def get_bot_content():
    # Prompt ko thoda aur simple kiya taaki Urdu clear aaye
    prompt = "Write a 40-second very funny Urdu story about Hulk and his Pakistani Ammi. Hulk is scared of Ammi's chappal. Format: STORY: [urdu text] SCENES: [5 short English image keywords]"
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
    # multilingual_v2 Urdu/Hindi ke liye best hai
    data = {
        "text": text, 
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with os.open("voice.mp3", os.O_CREAT | os.O_WRONLY) as f:
            os.write(f, response.content)
        return True
    else:
        print(f"ElevenLabs Error: {response.text}")
        return False

def download_images(keywords):
    valid_paths = []
    for i, k in enumerate(keywords[:5]):
        # Pakistani context for DALL-E style images
        full_p = f"3D Disney style Hulk with a Pakistani mother in a traditional house, {k}"
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
    print("🤖 Bot is starting...")
    story, scenes = get_bot_content()
    print("🎙️ Generating Voiceover...")
    if make_elevenlabs_audio(story):
        print("🖼️ Downloading Images...")
        imgs = download_images(scenes)
        print("🎬 Stitching Video...")
        create_video(imgs, "voice.mp3")
        print("✅ SUCCESS!")

if __name__ == "__main__":
    asyncio.run(start_bot())
