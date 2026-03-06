import os
import asyncio
import edge_tts
import requests
import google.generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- GEMINI v1beta SETUP ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_KEY)

# Gemini 1.5 Flash (v1beta version)
# Ye model abhi sabse stable hai automation ke liye
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voiceover.mp3")

def get_ai_content():
    # Long script prompt for 90 seconds video
    prompt = """Write a funny 90-second Hindi story about Hulk and his Indian Mom. 
    The story must be very detailed (350-400 words).
    Format exactly like this:
    STORY: [Hindi text]
    SCENES: [12 English image prompts separated by commas]"""
    
    # Model generation call
    response = model.generate_content(prompt)
    text = response.text
    
    try:
        story = text.split("STORY:")[1].split("SCENES:")[0].strip()
        prompts = text.split("SCENES:")[1].strip().split(",")
        return story, prompts
    except:
        return "Hulk ki mummy ne use belan se mara.", ["angry indian mom", "hulk crying"]

def download_images(prompts):
    img_list = []
    for i, p in enumerate(prompts[:12]):
        # Pollinations AI use kar rahe hain (Free & Fast)
        url = f"https://image.pollinations.ai/prompt/{p.strip().replace(' ', '%20')}?width=1080&height=1920&nologo=true"
        r = requests.get(url)
        name = f"step_{i}.jpg"
        with open(name, "wb") as f:
            f.write(r.content)
        img_list.append(name)
    return img_list

def create_video(images, audio_file):
    audio = AudioFileClip(audio_file)
    duration_per_img = audio.duration / len(images)
    clips = [ImageClip(img).set_duration(duration_per_img).crossfadein(0.5) for img in images]
    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio)
    # Output file
    final.write_videofile("hulk_funny_final.mp4", fps=24, codec="libx264")

async def start_process():
    try:
        print("🤖 Gemini v1beta (1.5 Flash) is generating story...")
        story, prompts = get_ai_content()
        print("🎙️ Creating Voiceover...")
        await generate_audio(story)
        print("🖼️ Downloading Images...")
        imgs = download_images(prompts)
        print("🎬 Final Video Editing...")
        create_video(imgs, "voiceover.mp3")
        print("✅ DONE! Video is ready.")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(start_process())
