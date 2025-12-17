"""Simple MJPEG generator using Picamera2 for use with FastAPI StreamingResponse.

Usage:
    from mjpeg_stream import mjpeg_generator
    return StreamingResponse(mjpeg_generator(), media_type='multipart/x-mixed-replace; boundary=FRAME')

This module creates a small output object with a Condition that Picamera2 writes
JPEG frames to. The generator yields proper multipart boundary + headers + frame bytes.
"""
from threading import Condition
import io

try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
except Exception:
    # Import error will be surfaced when attempting to start streaming.
    Picamera2 = None
    JpegEncoder = None
    FileOutput = None


class _MJPEGOutput(io.BufferedIOBase):
    """A simple BufferedIOBase implementation that stores the latest
    JPEG frame written by Picamera2 and notifies a Condition.

    FileOutput requires an object that is an instance of io.BufferedIOBase,
    otherwise it raises "Must pass io.BufferedIOBase".
    """
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def writable(self):
        return True

    def write(self, buf):
        # Picamera2 may provide a memoryview-like buffer; ensure bytes
        b = bytes(buf)
        with self.condition:
            self.frame = b
            self.condition.notify_all()
        # Return number of bytes written as expected by BufferedIOBase
        return len(b)


def mjpeg_generator(width: int = 640, height: int = 480, quality: int = 80):
    """Yield multipart MJPEG frames indefinitely.

    Yields bytes that are ready to be sent by a StreamingResponse.
    Caller is responsible for using media_type 'multipart/x-mixed-replace; boundary=FRAME'.
    """
    if Picamera2 is None:
        raise RuntimeError("picamera2 is not available in this Python environment")

    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (width, height)}))
    output = _MJPEGOutput()
    # Use default encoder; quality param available if needed by encoder
    encoder = JpegEncoder()
    picam2.start_recording(encoder, FileOutput(output))
    boundary = "FRAME"

    try:
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
            if not frame:
                continue
            header = (
                b"--" + boundary.encode("ascii") + b"\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame)).encode("ascii") + b"\r\n\r\n"
            )
            yield header + frame + b"\r\n"
    finally:
        try:
            picam2.stop_recording()
        except Exception:
            pass
