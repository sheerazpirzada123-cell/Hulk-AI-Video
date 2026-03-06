import os
import asyncio
import edge_tts
import requests
import random
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def get_free_story():
    # Pollinations AI for story text (No API Key)
    prompt = "Write a funny 60-second Hindi story about Hulk and his Indian Mom. Format: STORY: [hindi text] KEYWORDS: [5 simple English nouns separated by commas]"
    url = f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}"
    try:
        r = requests.get(url, timeout=30)
        text = r.text
        story = text.split("STORY:")[1].split("KEYWORDS:")[0].strip()
        keywords = text.split("KEYWORDS:")[1].strip().split(",")
        return story, [k.strip() for k in keywords]
    except:
        return "Hulk ki mummy ne use belan se mara.", ["hulk", "angry", "mom", "kitchen", "india"]

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voiceover.mp3")

def download_images(keywords):
    img_list = []
    # Keyword based images (Unsplash is very stable for downloads)
    for i, word in enumerate(keywords[:5]):
        url = f"https://source.unsplash.com/featured/1080x1920?{word.replace(' ', '')}"
        try:
            r = requests.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                name = f"image_{i}.jpg"
                with open(name, "wb") as f:
                    f.write(r.content)
                img_list.append(name)
                print(f"✅ Downloaded image for: {word}")
        except:
            print(f"❌ Failed to download: {word}")
    return img_list

def create_video(images, audio_file):
    if not images:
        raise Exception("Koi image download nahi hui!")
    
    audio = AudioFileClip(audio_file)
    # 5 images ko total audio length par divide karna
    duration_per_img = audio.duration / len(images)
    
    clips = [ImageClip(m).set_duration(duration_per_img).set_fps(24) for m in images]
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile("hulk_funny_final.mp4", fps=24, codec="libx264")

async def start_process():
    try:
        print("📝 Story generation...")
        story, keywords = get_free_story()
        print("🎙️ Audio generation...")
        await generate_audio(story)
        print("🖼️ Image downloading...")
        imgs = download_images(keywords)
        print("🎬 Video stitching...")
        create_video(imgs, "voiceover.mp3")
        print("✅ SUCCESS!")
    except Exception as e:
        print(f"❌ Final Error: {e}")

if __name__ == "__main__":
    asyncio.run(start_process())
