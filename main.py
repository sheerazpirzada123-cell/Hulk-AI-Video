import os, asyncio, edge_tts, requests, time
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# 1. Automatic Content Generation (Pakistani Theme)
def get_bot_content():
    prompt = "Write a 50-second funny Urdu/Hindi story about Hulk and his Pakistani Ammi. Format: STORY: [urdu text] SCENES: [6 short English image keywords]"
    url = f"https://text.pollinations.ai/{prompt.replace(' ', '%20')}"
    try:
        r = requests.get(url, timeout=30)
        story = r.text.split("STORY:")[1].split("SCENES:")[0].strip()
        scenes = r.text.split("SCENES:")[1].strip().split(",")
        return story, [s.strip() for s in scenes]
    except:
        return "Hulk ki Ammi ne use chappal dikhayi.", ["angry pakistani mother", "hulk scared"]

# 2. Automatic Voiceover
async def make_voice(text):
    # MadhurNeural works great for Urdu/Hindi
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("voice.mp3")

# 3. Automatic Image Generation & Validation
def download_images(keywords):
    valid_paths = []
    for i, k in enumerate(keywords[:6]):
        # Pakistani context added to prompts automatically
        full_prompt = f"3D Disney style Hulk with a Pakistani mother in traditional dress, {k}"
        url = f"https://image.pollinations.ai/prompt/{full_prompt.replace(' ', '%20')}?width=720&height=1280&seed={int(time.time())+i}&nologo=true"
        try:
            res = requests.get(url, timeout=20)
            raw = f"raw_{i}.jpg"
            with open(raw, "wb") as f: f.write(res.content)
            # Fixes the 'avcodec_send_packet' error from your screenshot
            with Image.open(raw) as img:
                img.convert("RGB").save(f"final_{i}.jpg", "JPEG")
                valid_paths.append(f"final_{i}.jpg")
        except: continue
    return valid_paths

# 4. Final Video Stitching
def create_bot_video(images, audio):
    aud = AudioFileClip(audio)
    duration = aud.duration / len(images)
    clips = [ImageClip(m).set_duration(duration).set_fps(24) for m in images]
    final = concatenate_videoclips(clips, method="compose").set_audio(aud)
    final.write_videofile("hulk_pakistani_ammi.mp4", fps=24, codec="libx264", audio_codec="aac")

async def start_bot():
    print("🤖 Bot is starting automation...")
    story, scenes = get_bot_content()
    await make_voice(story)
    imgs = download_images(scenes)
    create_bot_video(imgs, "voice.mp3")
    print("✅ Video Generated Successfully!")

if __name__ == "__main__":
    asyncio.run(start_bot())
