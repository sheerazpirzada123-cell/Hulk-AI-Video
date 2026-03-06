import os
import asyncio
import edge_tts
import requests
import time
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def get_free_content():
    # Story generate karne ke liye reliable prompt
    prompt = "Write a funny short 60-second Hindi story about Hulk and his Indian Mom. Format: STORY: [hindi text] SCENES: [8 English image prompts separated by commas]"
    url = f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}"
    try:
        response = requests.get(url, timeout=30)
        text = response.text
        story = text.split("STORY:")[1].split("SCENES:")[0].strip()
        prompts = text.split("SCENES:")[1].strip().split(",")
        return story, [p.strip() for p in prompts if len(p) > 5]
    except:
        return "Hulk ki mummy ne use belan mara.", ["angry indian mom", "hulk crying"]

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voiceover.mp3")

def download_and_fix_images(prompts):
    img_list = []
    for i, p in enumerate(prompts[:8]):
        # Seed change karne se har baar nayi image milti hai
        seed = int(time.time()) + i
        url = f"https://image.pollinations.ai/prompt/{p.replace(' ', '%20')}?width=1024&height=1024&seed={seed}&nologo=true"
        
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                with open(f"raw_{i}.jpg", "wb") as f:
                    f.write(r.content)
                
                # Image check aur conversion
                with Image.open(f"raw_{i}.jpg") as img:
                    img.convert('RGB').save(f"fixed_{i}.jpg", "JPEG")
                    img_list.append(f"fixed_{i}.jpg")
                    print(f"✅ Image {i} ready")
        except Exception as e:
            print(f"⚠️ Skip image {i}: {e}")
            
    return img_list

def create_video(images, audio_file):
    if not images:
        raise Exception("Koi image download nahi hui!")
    
    audio = AudioFileClip(audio_file)
    duration_per_img = audio.duration / len(images)
    clips = [ImageClip(img).set_duration(duration_per_img) for img in images]
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile("hulk_funny_final.mp4", fps=24, codec="libx264", audio_codec="aac")

async def start_process():
    try:
        print("🤖 Story generation...")
        story, prompts = get_free_content()
        print("🎙️ Audio generation...")
        await generate_audio(story)
        print("🖼️ Image processing...")
        imgs = download_and_fix_images(prompts)
        print("🎬 Final video stitching...")
        create_video(imgs, "voiceover.mp3")
        print("✅ MUBARAK HO! Video ban gayi.")
    except Exception as e:
        print(f"❌ Final Error: {e}")

if __name__ == "__main__":
    asyncio.run(start_process())
