import os
import asyncio
import edge_tts
import requests
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def get_free_content():
    prompt = "Write a funny 90-second Hindi story about Hulk and his Indian Mom. Format: STORY: [hindi text] SCENES: [10 English image prompts separated by commas]"
    url = f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}"
    response = requests.get(url)
    text = response.text
    try:
        story = text.split("STORY:")[1].split("SCENES:")[0].strip()
        prompts = text.split("SCENES:")[1].strip().split(",")
        return story, prompts
    except:
        return "Hulk ki mummy ne use belan dikhaya.", ["angry indian mom", "hulk scared"]

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voiceover.mp3")

def download_and_fix_images(prompts):
    img_list = []
    for i, p in enumerate(prompts[:10]):
        url = f"https://image.pollinations.ai/prompt/{p.strip().replace(' ', '%20')}?width=1024&height=1024&nologo=true"
        r = requests.get(url)
        temp_name = f"raw_{i}.jpg"
        final_name = f"fixed_{i}.jpg"
        
        with open(temp_name, "wb") as f:
            f.write(r.content)
        
        # --- IMAGE FIXING LOGIC ---
        # Isse 'avcodec_send_packet' wala error khatam ho jayega
        try:
            with Image.open(temp_name) as img:
                rgb_img = img.convert('RGB')
                rgb_img.save(final_name, "JPEG")
            img_list.append(final_name)
        except Exception as e:
            print(f"Skipping bad image {i}: {e}")
            
    return img_list

def create_video(images, audio_file):
    audio = AudioFileClip(audio_file)
    duration_per_img = audio.duration / len(images)
    clips = [ImageClip(img).set_duration(duration_per_img) for img in images]
    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio)
    # FPS fix aur simple codec use kar rahe hain
    final.write_videofile("hulk_funny_final.mp4", fps=24, codec="libx264", audio_codec="aac")

async def start_process():
    try:
        print("🤖 Story likh raha hai...")
        story, prompts = get_free_content()
        print("🎙️ Awaaz ban rahi hai...")
        await generate_audio(story)
        print("🖼️ Images fix ho rahi hain...")
        imgs = download_and_fix_images(prompts)
        print("🎬 Video processing...")
        create_video(imgs, "voiceover.mp3")
        print("✅ SUCCESS!")
    except Exception as e:
        print(f"❌ Final Error: {e}")

if __name__ == "__main__":
    asyncio.run(start_process())
