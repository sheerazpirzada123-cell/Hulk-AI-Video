import os
import asyncio
import edge_tts
import requests
import google.generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- SETUP ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voiceover.mp3")

def get_ai_content():
    prompt = """Write a funny 90-second Hindi story about Hulk and his Indian Mom. 
    Format:
    STORY: [The Hindi story]
    SCENES: [12 English image prompts separated by commas]"""
    response = model.generate_content(prompt)
    text = response.text
    try:
        story = text.split("STORY:")[1].split("SCENES:")[0].strip()
        prompts = text.split("SCENES:")[1].strip().split(",")
        return story, prompts
    except:
        return "Hulk ko mummy ne mara.", ["hulk crying", "angry indian mom"]

def download_images(prompts):
    img_list = []
    for i, p in enumerate(prompts[:12]):
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
    clips = []
    for img in images:
        # Pillow install hone ke baad ye error nahi dega
        clip = ImageClip(img).set_duration(duration_per_img)
        clips.append(clip)
    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio)
    final.write_videofile("hulk_funny_final.mp4", fps=24, codec="libx264")

async def start_process():
    try:
        print("🤖 Generating with Gemini 1.5 Flash...")
        story, prompts = get_ai_content()
        await generate_audio(story)
        imgs = download_images(prompts)
        create_video(imgs, "voiceover.mp3")
        print("✅ Success!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(start_process())
