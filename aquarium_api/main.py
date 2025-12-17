from fastapi import FastAPI, Request, HTTPException
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware

import sys
import subprocess
from subprocess import PIPE
import requests

from schema import schema
import io
import time
import logging
from threading import Condition
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path
import requests
# Import mjpeg_generator in a way that works whether this module is run
# as a package (uvicorn aquarium_api.main:app) or as a script/cwd module
try:
    from .mjpeg_stream import mjpeg_generator
except Exception:
    try:
        from mjpeg_stream import mjpeg_generator
    except Exception:
        from aquarium_api.mjpeg_stream import mjpeg_generator


# (6) FastAPIインスタンス作成
app = FastAPI()

# CORS設定の追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて許可するオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/sample")
async def sample():
    """Serve the example HTML file bundled with this package.

    Uses an absolute path so it works whether the app is started from
    the repo root or from inside the `aquarium_api` directory.
    """
    p = Path(__file__).resolve().parent / "sample.html"
    if not p.exists():
        raise HTTPException(status_code=404, detail="sample.html not found")
    return FileResponse(str(p), media_type="text/html")



# (7) レスポンス出力
@app.get("/")
async def index():
    return {"message": "Welcome to the Aquarium API"}



app.add_route("/graphql", GraphQL(schema))


@app.get("/mjpeg")
def mjpeg():
    """Return an MJPEG stream sourced from Picamera2.

    The response uses content type 'multipart/x-mixed-replace; boundary=FRAME'.
    """
    # Proxy to local camera process (must be started separately)
    camera_url = 'http://127.0.0.1:8010/stream.mjpg'
    try:
        resp = requests.get(camera_url, stream=True, timeout=5)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Camera process not reachable: {e}")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Camera process returned {resp.status_code}")

    def stream_from_camera(r):
        try:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        finally:
            try:
                r.close()
            except Exception:
                pass

    return StreamingResponse(stream_from_camera(resp), media_type=resp.headers.get('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME'))
