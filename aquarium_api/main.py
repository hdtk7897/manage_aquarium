from fastapi import FastAPI, Request
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
from fastapi.responses import StreamingResponse


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


# Configuration for external camera process
CAMERA_PROC_PATH = '/home/hdtk7897/manage_aquarium/python/mjpeg_server.py'
CAMERA_URL = 'http://127.0.0.1:8010/stream.mjpg'


def ensure_camera_process_running():
    """Try to connect to the local camera server; if unavailable, start it as a separate process."""
    try:
        r = requests.get(CAMERA_URL, stream=True, timeout=1)
        if r.status_code == 200:
            return
    except Exception:
        pass

    # Start the camera server process (detached). Use the same python executable.
    try:
        subprocess.Popen([sys.executable, CAMERA_PROC_PATH], stdout=PIPE, stderr=PIPE, start_new_session=True)
    except Exception as e:
        # If starting fails, log and continue; the endpoint will retry when clients connect
        logging.getLogger(__name__).exception('Failed to start camera process: %s', e)




def get_frame():
    """Proxy frames from the local mjpeg server and yield raw multipart bytes to the client.

    This generator will reconnect on errors.
    """
    logger = logging.getLogger(__name__)
    backoff = 1
    max_backoff = 16
    while True:
        try:
            # Ensure camera process is running (best-effort)
            ensure_camera_process_running()

            with requests.get(CAMERA_URL, stream=True, timeout=5) as resp:
                if resp.status_code != 200:
                    logger.warning('Camera server returned %s', resp.status_code)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
                    continue

                backoff = 1
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
        except Exception:
            logger.exception('Error proxying frames — retrying in %s seconds', backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
            continue



# (7) レスポンス出力
@app.get("/")
async def index():
    return {"message": "Welcome to the Aquarium API"}

@app.get("/mjpeg", response_class=StreamingResponse)
def mjpeg(request: Request):
    try:
        frames = get_frame()
        response = StreamingResponse(
            frames,
            headers={
                "Cache-Control": "no-cache, private",
                "Pragma": "no-cache",
            },
            media_type="multipart/x-mixed-replace; boundary=frame",
        )
        return response
    except Exception as e:
        print("Error! Route")


app.add_route("/graphql", GraphQL(schema))
