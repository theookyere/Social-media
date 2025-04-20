import os
import uuid
from flask import Flask, render_template, request, send_file, abort
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if YoutubeDL is None:
        return render_template("index.html", error="Missing dependency 'yt-dlp'. Please install with `pip install yt-dlp`.")
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return render_template("index.html", error="Please provide a URL.")
        filename = f"{uuid.uuid4()}"
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, filename + ".%(ext)s"),
            "format": "best",
            "socket_timeout": 10,
            "noplaylist": True,
            "quiet": True
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            ext = info.get("ext")
            filepath = os.path.join(DOWNLOAD_FOLDER, filename + f".{ext}")
            return send_file(filepath, as_attachment=True)
        except Exception as e:
            # Fallback: parse Open Graph tags and generic img/video tags
            try:
                resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                media_urls = []
                # Open Graph tags
                for prop in ('og:video', 'og:video:url', 'og:image', 'og:image:url'):
                    tag = soup.find('meta', property=prop)
                    if tag and tag.get('content'):
                        media_urls.append(tag['content'])
                # Generic tags
                if not media_urls:
                    for img in soup.find_all('img', src=True):
                        media_urls.append(img['src'])
                    for video in soup.find_all('video'):
                        src = video.get('src')
                        if src:
                            media_urls.append(src)
                        for source in video.find_all('source'):
                            if source.get('src'):
                                media_urls.append(source['src'])
                if not media_urls:
                    raise e
                media_url = urljoin(url, media_urls[0])
                r2 = requests.get(media_url, stream=True, timeout=10)
                ext = media_url.split('?')[0].split('.')[-1]
                filepath = os.path.join(DOWNLOAD_FOLDER, filename + f'.{ext}')
                with open(filepath, 'wb') as f:
                    for chunk in r2.iter_content(1024*1024):
                        if chunk:
                            f.write(chunk)
                return send_file(filepath, as_attachment=True)
            except Exception as e2:
                return render_template('index.html', error=f'Could not download media: {e2}')
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
