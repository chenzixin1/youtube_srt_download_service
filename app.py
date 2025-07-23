from flask import Flask, request, send_file, jsonify, abort
import yt_dlp
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
load_dotenv()
import webvtt
import re
import subprocess

app = Flask(__name__)

# 限流：每个 IP 每分钟最多 10 次
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY environment variable not set")

YOUTUBE_URL_PATTERN = re.compile(r'^https?://(www\.)?(youtube\.com|youtu\.be)/')

@app.before_request
def check_api_key_and_headers():
    # API Key 校验
    if request.args.get('key') != API_KEY:
        abort(401)
    # 移除 User-Agent 检查

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/srt', methods=['GET'])
def get_srt():
    """
    这个接口会返回 SRT 字幕文件。
    实现方式如下：
    1. 获取 url 参数。
    2. 用 yt_dlp 下载字幕（不下载视频）。
    3. 如果生成了 SRT 文件，则用 Flask 的 send_file 返回该文件，as_attachment=True 表示作为附件下载。
    4. 最后删除本地生成的 SRT 文件。
    """
    url = request.args.get('url')
    if not url or not YOUTUBE_URL_PATTERN.match(url):
        return jsonify({'error': 'Invalid or missing url parameter'}), 400

    output_prefix = 'subtitle'
    vtt_path = f'{output_prefix}.en.vtt'
    srt_path = f'{output_prefix}.srt'
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitlesformat': 'best',
        'skip_download': True,
        'outtmpl': output_prefix,
        'subtitleslangs': ['en'],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        # 如果有 vtt，转为 srt
        if os.path.exists(vtt_path):
            webvtt.read(vtt_path).save_as_srt(srt_path)
        # 返回 srt 文件
        if os.path.exists(srt_path):
            return send_file(srt_path, as_attachment=True)
        else:
            return jsonify({'error': 'SRT not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        for f in [vtt_path, srt_path]:
            if os.path.exists(f):
                os.remove(f)

@app.route('/about', methods=['GET'])
def about():
    try:
        git_version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
    except Exception:
        git_version = 'unknown'
    return jsonify({
        'service': 'YouTube SRT Download Service',
        'description': '提供 YouTube 视频英文字幕（含自动生成字幕）下载，自动转为 SRT 格式。',
        'version': '2024-07-22',
        'git_commit': git_version,
        'author': 'chenzixin1',
        'github': 'https://github.com/chenzixin1/youtube_srt_download_service'
    })

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube SRT Download Service")
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on (default: 5000)')
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port) 