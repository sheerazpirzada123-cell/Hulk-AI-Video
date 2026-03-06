import os
import requests
import io
from PIL import Image
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "TxGEqnSAs9dnFT47v3tM"
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_VIDEO = "hulk_bot_final.mp4"
TEMP_DIR = "temp_images"

def fetch_story_and_keywords():
    """Fetches story and keywords from Pollinations Text API."""
    prompt = "Write a funny Urdu/Hindi story about Hulk and a strict Pakistani mother. After the story, provide 5 comma-separated image keywords for scenes. Separate keywords with '###KEYWORDS###'."
    
    try:
        response = requests.get(f"https://text.pollinations.ai/{prompt}")
        response.raise_for_status()
        content = response.text
        
        # Parse keywords
        if "###KEYWORDS###" in content:
            story, keywords_part = content.split("###KEYWORDS###", 1)
            keywords = [k.strip() for k in keywords_part.split(",")]
        else:
            # Fallback if parsing fails
            story = content
            keywords = ["Hulk", "Pakistani Mother", "Funny Scene", "Hulk Scared", "Hulk Eating"]
            
        return story, keywords[:5]
    except Exception as e:
        print(f"Error fetching story: {e}")
        return "Default Story", ["Hulk", "Mother", "Funny", "Scene", "Action"]

def generate_audio(story):
    """Generates Urdu audio using ElevenLabs API."""
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is missing in environment variables.")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": story,
        "model_id": MODEL_ID,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        audio_path = "temp_audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        return audio_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        raise

def download_and_process_images(keywords):
    """Downloads 5 images and converts them to RGB JPEG."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    image_paths = []
    
    for i, keyword in enumerate(keywords):
        img_url = f"https://image.pollinations.ai/prompt/{keyword}?width=1080&height=1920&nologo=true"
        img_path = os.path.join(TEMP_DIR, f"frame_{i}.jpg")
        
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            
            # Open with Pillow
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB and save as JPEG to avoid codec errors
            img = img.convert('RGB')
            img.save(img_path, format='JPEG', quality=85)
            
            image_paths.append(img_path)
            print(f"Downloaded and processed image {i+1}")
            
        except Exception as e:
            print(f"Error downloading image {i+1}: {e}")
            # Fallback: Use the last successful image or a placeholder to prevent crash
            if image_paths:
                image_paths.append(image_paths[-1])
            else:
                # Create a blank black image if all fail
                blank = Image.new('RGB', (1080, 1920), color='black')
                blank.save(img_path, format='JPEG')
                image_paths.append(img_path)
                
    return image_paths

def create_video(audio_path, image_paths):
    """Combines images and audio into a video."""
    try:
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        segment_duration = total_duration / 5
        
        clips = []
        for img_path in image_paths:
            img_clip = ImageClip(img_path).set_duration(segment_duration)
            clips.append(img_clip)
        
        final_clip = CompositeVideoClip(clips)
        final_clip = final_clip.set_audio(audio)
        
        final_clip.write_videofile(
            OUTPUT_VIDEO, 
            codec='libx264', 
            fps=24, 
            audio_codec='aac',
            temp_audiofile='temp_audio.m4a',
            remove_temp=True
        )
        print(f"Video saved as {OUTPUT_VIDEO}")
        
    except Exception as e:
        print(f"Error creating video: {e}")
        raise

def main():
    print("Starting Hulk Bot Generation...")
    
    # 1. Get Content
    story, keywords = fetch_story_and_keywords()
    print(f"Story fetched. Keywords: {keywords}")
    
    # 2. Generate Audio
    audio_path = generate_audio(story)
    print("Audio generated.")
    
    # 3. Download & Process Images
    image_paths = download_and_process_images(keywords)
    print("Images processed.")
    
    # 4. Create Video
    create_video(audio_path, image_paths)
    
    # Cleanup (Optional)
    # os.remove(audio_path)
    # for p in image_paths: os.remove(p)
    
    print("Done!")

if __name__ == "__main__":
    main()
