import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/get_video', methods=['POST'])
def get_video():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Analyzing Link: {video_url}")

    # Identify where the link came from
    is_facebook = 'facebook.com' in video_url or 'fb.watch' in video_url or 'fb.gg' in video_url
    is_instagram = 'instagram.com' in video_url

    ydl_opts = {
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            
            video_options = []

            for f in formats:
                format_id = f.get('format_id', '').lower()
                ext = f.get('ext', '')

                # 1. THE FACEBOOK RULE
                if is_facebook:
                    if format_id in ['sd', 'hd']:
                        quality_name = "HD Quality" if format_id == 'hd' else "Standard Quality"
                        video_options.append({"quality": quality_name, "url": f.get('url')})
                
                # 2. THE INSTAGRAM RULE
                elif is_instagram:
                    if ext == 'mp4':
                        # Instagram videos are pre-mixed, so any mp4 works
                        video_options.append({"quality": "Instagram Video", "url": f.get('url')})

            # Clean up Instagram duplicates (we just want to offer the best one)
            if is_instagram and len(video_options) > 0:
                video_options = [video_options[-1]]

            return jsonify({
                "title": info.get('title', 'Video'),
                "videos": video_options,
                "audios": [] # Skipping separate audio for IG to keep it simple
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

