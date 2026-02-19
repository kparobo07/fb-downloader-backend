from flask import Flask, request, jsonify
import yt_dlp
import os
app = Flask(__name__)

@app.route('/get_video', methods=['POST'])
def get_video():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Analyzing: {video_url}")

    ydl_opts = {
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            
            video_options = []
            audio_options = []

            for f in formats:
                format_id = f.get('format_id', '').lower()

                # 1. Catch Audio Only files
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_options.append({
                        "quality": "Audio Only",
                        "url": f.get('url')
                    })
                
                # 2. BULLETPROOF FACEBOOK CHECK: Only grab the pre-mixed 'sd' and 'hd' files
                elif format_id in ['sd', 'hd']:
                    quality_name = "HD Quality" if format_id == 'hd' else "Standard Quality"
                    video_options.append({
                        "quality": quality_name,
                        "url": f.get('url')
                    })

            # Clean up the audio list to just show one good audio track
            if len(audio_options) > 0:
                audio_options = [audio_options[-1]]

            return jsonify({
                "title": info.get('title'),
                "videos": video_options,
                "audios": audio_options
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

# ... (Keep all your other yt-dlp code exactly the same) ...

if __name__ == '__main__':
    # Cloud servers assign a random port, this catches it
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)