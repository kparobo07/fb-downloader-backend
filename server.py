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

    print(f"Analyzing Universal Link: {video_url}")

    # Check if the link is from Facebook
    is_facebook = 'facebook.com' in video_url or 'fb.watch' in video_url or 'fb.gg' in video_url

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
            added_qualities = set()

            for f in formats:
                format_id = f.get('format_id', '').lower()
                ext = f.get('ext', '')
                vcodec = f.get('vcodec')
                acodec = f.get('acodec')
                height = f.get('height')

                # 1. Grab Audio Only
                if vcodec == 'none' and acodec != 'none':
                    audio_options.append({"quality": "Audio Only", "url": f.get('url')})
                
                # 2. FACEBOOK ROUTE: Grab 'sd' and 'hd' only
                if is_facebook:
                    if format_id in ['sd', 'hd']:
                        quality_name = "HD Quality" if format_id == 'hd' else "Standard Quality"
                        video_options.append({"quality": quality_name, "url": f.get('url')})
                
                # 3. UNIVERSAL ROUTE (TikTok, IG, X): Grab any mp4 with both audio & video
                else:
                    if vcodec != 'none' and acodec != 'none' and ext == 'mp4':
                        if height and height not in added_qualities:
                            video_options.append({"quality": f"{height}p", "url": f.get('url')})
                            added_qualities.add(height)

            # Sort Universal videos highest to lowest quality
            if not is_facebook:
                video_options.sort(key=lambda x: int(x['quality'].replace('p','')), reverse=True)

            if len(audio_options) > 0:
                audio_options = [audio_options[-1]]

            return jsonify({
                "title": info.get('title'),
                "videos": video_options,
                "audios": audio_options
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
