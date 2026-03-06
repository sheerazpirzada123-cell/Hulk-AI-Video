import os
import asyncio
import edge_tts
import requests
import google.generativeai as genai

# MoviePy imports ko handle karne ka naya tarika
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- SETUP ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voiceover.mp3")

def get_ai_content():
    prompt = "Write a funny 90-second Hindi story about Hulk and his Indian Mom. Format: STORY: [text] SCENES: [12 English prompts separated by commas]"
    response = model.generate_content(prompt)
    text = response.text
    story = text.split("STORY:")[1].split("SCENES:")[0].strip()
    prompts = text.split("SCENES:")[1].strip().split(",")
    return story, prompts

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
    clips = [ImageClip(img).set_duration(duration_per_img).crossfadein(0.5) for img in images]
    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio)
    final.write_videofile("hulk_funny_final.mp4", fps=24, codec="libx264")

async def start_process():
    story, prompts = get_ai_content()
    await generate_audio(story)
    imgs = download_images(prompts)
    create_video(imgs, "voiceover.mp3")

if __name__ == "__main__":
    asyncio.run(start_process())
