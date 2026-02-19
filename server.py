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

    # THE FIX: Clean the Instagram tracking junk off the link
    if 'instagram.com' in video_url:
        video_url = video_url.split('?')[0]

    print(f"Analyzing Link: {video_url}")

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

                if is_facebook:
                    if format_id in ['sd', 'hd']:
                        quality_name = "HD Quality" if format_id == 'hd' else "Standard Quality"
                        video_options.append({"quality": quality_name, "url": f.get('url')})
                
                elif is_instagram:
                    if ext == 'mp4':
                        video_options.append({"quality": "Instagram Video", "url": f.get('url')})

            if is_instagram and len(video_options) > 0:
                video_options = [video_options[-1]]

            return jsonify({
                "title": info.get('title', 'Video'),
                "videos": video_options,
                "audios": [] 
            })

    except Exception as e:
        # This prints the EXACT reason it failed to your Render logs
        print(f"CRASH REPORT: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
