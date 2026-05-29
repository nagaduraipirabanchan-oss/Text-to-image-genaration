import json
import os
import requests
import time
import random
import urllib.parse
from flask import Flask, render_template, request, jsonify, session
from database import init_db, add_art, get_user_gallery, get_all_stats

app = Flask(__name__)
app.secret_key = "visual_pro_secret"

# Initialize structural database
init_db()

# --- Helper Function to Update JSON Stats ---
def update_image_count():
    stats_file = 'stats.json'
    # Check if file exists, if not create one with default value
    if not os.path.exists(stats_file):
        with open(stats_file, 'w') as f:
            json.dump({"total_images": 12544}, f)

    # Read current count
    with open(stats_file, 'r') as f:
        data = json.load(f)
    
    # Increment count
    data['total_images'] += 1
    
    # Save back to file
    with open(stats_file, 'w') as f:
        json.dump(data, f)
    
    return data['total_images']

@app.route('/')
def index():
    # Fetching the live count to display on the landing page
    stats_file = 'stats.json'
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            data = json.load(f)
            current_count = data.get('total_images', 12544)
    else:
        current_count = 12544
        
    return render_template('index.html', live_count=current_count)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    style = data.get('style', 'Realistic').lower() 
    resolution = data.get('resolution')
    should_enhance = data.get('enhance', True)

    if not prompt:
        return jsonify({'success': False, 'error': 'Prompt context data validation failure.'})

    # AI Prompt Enhancer Logic
    if should_enhance:
        enhancers_map = {
            "realistic": "ultra realistic cinematic look, 8k resolution detailed textures, professional volumetric lighting, ray tracing, atmospheric mist",
            "cyberpunk": "neon hyper glowing grid accents, cyberpunk aesthetic city profile background, retro cyberpunk lighting",
            "anime": "magical 3d anime style asset render, trending on artstation concept illustration, studio production level",
            "oil painting": "classical oil paint texture layers style, visible canvas micro structures brush strokes",
            "pixel art": "vibrant retro 8-bit accurate pixel art design blueprint asset, sharp squares separation grid",
            "3d render": "highly detailed complex 3d asset design illustration, octane rendering setup parameters"
        }
        quality_boost = enhancers_map.get(style, "masterpiece quality structure definition detail")
        final_prompt = f"{prompt}, styled as {style}, {quality_boost}"
    else:
        final_prompt = f"{prompt}, {style} style specification"
    
    # Resolution Handling
    width, height = 1024, 1024
    if resolution == "512x512":
        width, height = 512, 512
    elif resolution == "16:9":
        width, height = 1280, 720

    encoded_query = urllib.parse.quote(final_prompt)
    seed = random.randint(1, 9999999)
    img_url = f"https://image.pollinations.ai/p/{encoded_query}?width={width}&height={height}&seed={seed}&nologo=true"

    try:
        response = requests.get(img_url, timeout=35)
        if response.status_code == 200:
            filename = f"art_{int(time.time())}_{random.randint(100,999)}.jpg"
            path = os.path.join('static/outputs', filename)
            
            os.makedirs('static/outputs', exist_ok=True)
            
            with open(path, 'wb') as f:
                f.write(response.content)
            
            # 1. Save to SQLite database
            add_art(0, prompt, style, f"/static/outputs/{filename}")
            
            # 2. Update LIVE counter in JSON
            new_total = update_image_count()
            
            return jsonify({
                'success': True, 
                'img': f"/static/outputs/{filename}",
                'enhanced_prompt': final_prompt,
                'resolution': f"{width}x{height}",
                'new_total_count': new_total  # Sending this back to frontend
            })
        else:
            return jsonify({'success': False, 'error': f"AI Node error: {response.status_code}"})
    except Exception as err:
        return jsonify({'success': False, 'error': f"Latency timeout: {str(err)}"})

@app.route('/api/gallery')
def gallery_data():
    return jsonify(get_user_gallery())

@app.route('/api/stats')
def stats():
    # Option to fetch all stats if needed via API
    return jsonify(get_all_stats())

if __name__ == '__main__':
    app.run(debug=True)