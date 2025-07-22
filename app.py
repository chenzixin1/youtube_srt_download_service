from flask import Flask, request, send_file, jsonify, abort
import yt_dlp
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# 限流：每个 IP 每分钟最多 10 次
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY environment variable not set")

@app.before_request
def check_api_key():
    if request.args.get('key') != API_KEY:
        abort(401)

@app.route('/srt', methods=['GET'])
def get_srt():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    output_path = 'subtitle.srt'
    ydl_opts = {
        'writesubtitles': True,
        'subtitlesformat': 'srt',
        'skip_download': True,
        'outtmpl': output_path,
        'subtitleslangs': ['zh-Hans', 'zh-Hant', 'en', 'zh'],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'SRT not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 