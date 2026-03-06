import os
import asyncio
import edge_tts
import requests
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# --- 100% FREE AI SETUP (No API Key Needed) ---
def get_free_ai_content():
    # Hum Pollinations AI use kar rahe hain text ke liye
    prompt = "Write a funny 90-second Hindi story about Hulk and his Indian Mom. Format: STORY: [hindi text] SCENES: [12 English image prompts separated by commas]"
    url = f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}"
    
    response = requests.get(url)
    text = response.text
    
    try:
        # Text ko split karna
        if "STORY:" in text and "SCENES:" in text:
            story = text.split("STORY:")[1].split("SCENES:")[0].strip()
            prompts = text.split("SCENES:")[1].strip().split(",")
        else:
            # Fallback agar AI format follow na kare
            story = "Hulk ki mummy ne use belan se mara kyunki wo kamra saaf nahi kar raha tha."
            prompts = ["angry indian mom", "hulk crying", "funny indian house"]
        return story, prompts
    except:
        return "Hulk aur uski mummy ki ladayi.", ["hulk", "mom"]

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voiceover.mp3")

def download_images(prompts):
    img_list = []
    for i, p in enumerate(prompts[:12]):
        # Pollinations AI for Images
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
    try:
        print("🤖 Free AI Story likh raha hai...")
        story, prompts = get_free_ai_content()
        print("🎙️ Awaaz ban rahi hai...")
        await generate_audio(story)
        print("🖼️ Images download ho rahi hain...")
        imgs = download_images(prompts)
        print("🎬 Video edit ho rahi hai...")
        create_video(imgs, "voiceover.mp3")
        print("✅ SUCCESS! Video Ready.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(start_process())
