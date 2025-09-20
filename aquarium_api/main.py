from fastapi import FastAPI, Request
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

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


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output))




def get_frame():
    logger = logging.getLogger(__name__)
    backoff = 1
    max_backoff = 16
    # Keep the generator alive and retry on errors with exponential backoff
    while True:
        try:
            # Reset backoff on successful loop entry
            backoff = 1
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                    # Skip if we don't have a frame yet
                    if frame is None:
                        continue
                    yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        except Exception:
            # Log the exception and retry after sleeping
            logger.exception("Error reading frames — retrying in %s seconds", backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
            # continue to retry



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
