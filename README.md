# Social Media Downloader

A Flask web app to download videos and images from YouTube, Facebook, Instagram, TikTok, LinkedIn, and more.

## Features
- Paste any supported URL and download videos/images.
- Uses yt-dlp for best compatibility.
- Fallback to Open Graph/image/video scraping for sites not supported by yt-dlp.

## Deploying on Fly.io

1. [Install Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Login: `flyctl auth login`
3. In this folder, run:

    flyctl launch --name social-media-downloader --now

4. When prompted, set the internal port to `8080` (Fly expects your app to listen on 8080).
5. Set up a `fly.toml` if needed (Fly CLI will guide you).
6. Set the following environment variable in your Fly dashboard or `fly.toml`:

    [[services.ports]]
      handlers = ["http"]
      port = 80
      force_https = true

    [[services.ports]]
      handlers = ["tls", "http"]
      port = 443

    [env]
      PORT = "8080"

7. Deploy updates with:

    flyctl deploy

## Notes
- Make sure your app binds to `0.0.0.0` and port `8080` (see below).
- For large downloads, ensure your Fly.io plan supports the needed bandwidth and storage.

## Modifications for Fly.io
In `app.py`, change:

```
app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
```

to:

```
import os
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port, debug=False)
```

This allows Fly.io to set the port dynamically.
