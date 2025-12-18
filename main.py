from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "ok", "service": "ATechDown Youtube Engine"}

@app.post("/resolve")
def resolve_video(url: str = Body(..., embed=True)):
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # We only want metadata & direct links
            'youtube_include_dash_manifest': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info
            info = ydl.extract_info(url, download=False)
            
            # Process formats (filter for usable ones)
            formats = []
            for f in info.get('formats', []):
                # Filter out dash chunks usually, keep direct mp4/webm with both audio+video or separate
                # For simplicity, we pass all valid ones
                if f.get('url'):
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution'),
                        'filesize': f.get('filesize'),
                        'url': f.get('url'),
                        'note': f.get('format_note'),
                        'vcodec': f.get('vcodec'),
                        'acodec': f.get('acodec')
                    })
            
            # Sort formats: best video quality first
            formats.sort(key=lambda x: x.get('filesize') or 0, reverse=True)

            return {
                "success": True,
                "data": {
                    "id": info.get('id'),
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "thumbnail": info.get('thumbnail'),
                    "author": info.get('uploader'),
                    "view_count": info.get('view_count'),
                    "formats": formats
                }
            }

    except Exception as e:
        print(f"Error resolving {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
