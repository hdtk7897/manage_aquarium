#!/usr/bin/python3

# Mostly copied from https://picamera.readthedocs.io/en/release-1.13/recipes2.html
# Run this script, then point a web browser at http:<this-ip-address>:8000
# Note: needs simplejpeg to be installed (pip3 install simplejpeg).

import io
import logging
import socketserver
import subprocess
from pathlib import Path
from http import server
from threading import Condition
from typing import Optional

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Configure logging to show details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

PORT=8010
#VIDEO_DIR = Path('/home/hdtk7897/manage_aquarium/videos')
VIDEO_DIR = Path('/mnt/nas/videos')
SEGMENT_SECONDS = 600
FPS = 15


class VideoSegmentWriter:
    def __init__(self, output_dir: Path, segment_seconds: int = 600, fps: int = 15):
        self.output_dir = output_dir
        self.segment_seconds = segment_seconds
        self.fps = fps
        self.proc = None
        self.frame_count = 0
        logger.debug(f'Initializing VideoSegmentWriter: output_dir={output_dir}, segment_seconds={segment_seconds}, fps={fps}')
        self._start()

    def _start(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f'Video directory created/verified: {self.output_dir}')
        logger.info(f'Directory permissions: {oct(self.output_dir.stat().st_mode)[-3:]}')
        
        output_pattern = str(self.output_dir / '%Y%m%d_%H%M%S.mp4')
        cmd = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'warning',
            '-f', 'mjpeg',
            '-r', str(self.fps),
            '-i', 'pipe:0',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '23',
            '-f', 'segment',
            '-segment_time', str(self.segment_seconds),
            '-reset_timestamps', '1',
            '-strftime', '1',
            output_pattern,
        ]
        logger.debug(f'FFmpeg command: {" ".join(cmd)}')
        logger.debug(f'Output pattern: {output_pattern}')
        
        try:
            self.proc = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f'FFmpeg process started: PID={self.proc.pid}')
        except FileNotFoundError:
            logger.error('ffmpeg command not found; video output disabled')
            self.proc = None
        except Exception as e:
            logger.error(f'Failed to start ffmpeg: {e}; video output disabled')
            self.proc = None

    def write(self, jpeg_bytes: bytes):
        self.frame_count += 1
        if self.frame_count % 150 == 1:  # Log every 10 seconds at 15 fps
            logger.debug(f'Frame count: {self.frame_count}, FFmpeg process alive: {self.proc.poll() if self.proc else False}')
        
        if self.proc is None or self.proc.stdin is None:
            if self.frame_count == 1:
                logger.warning('FFmpeg process not available for video writing')
            return
        
        try:
            self.proc.stdin.write(jpeg_bytes)
            self.proc.stdin.flush()
        except BrokenPipeError:
            logger.error('ffmpeg pipe closed; video output disabled')
            self.proc = None
        except Exception as e:
            logger.error(f'Unexpected error while writing to ffmpeg: {e}')

    def close(self):
        logger.info('Closing VideoSegmentWriter')
        if self.proc is None:
            return
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
            self.proc.wait(timeout=5)
            logger.info(f'FFmpeg process closed gracefully. Total frames written: {self.frame_count}')
        except Exception as e:
            logger.error(f'Error closing ffmpeg: {e}')
            self.proc.kill()


class StreamingOutput(io.BufferedIOBase):
    def __init__(self, video_writer: Optional[VideoSegmentWriter] = None):
        self.frame = None
        self.condition = Condition()
        self.video_writer = video_writer
        self.frame_count = 0
        logger.info('StreamingOutput initialized')

    def write(self, buf):
        self.frame_count += 1
        if self.frame_count % 150 == 0:  # Log every 10 seconds at 15 fps
            logger.debug(f'StreamingOutput.write() called - frame {self.frame_count}, buf size: {len(buf)} bytes')
        
        if self.video_writer:
            self.video_writer.write(buf)
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


picam2 = Picamera2()
logger.info('Picamera2 initialized')

picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
logger.info('Picamera2 configured: 640x480')

video_writer = VideoSegmentWriter(VIDEO_DIR, SEGMENT_SECONDS, FPS)
logger.info('VideoSegmentWriter created')

output = StreamingOutput(video_writer=video_writer)
logger.info('StreamingOutput created')

picam2.start_recording(JpegEncoder(), FileOutput(output))
logger.info('Picamera2 recording started')

try:
    address = ('', PORT)
    server = StreamingServer(address, StreamingHandler)
    logger.info(f'Starting HTTP server on port {PORT}')
    server.serve_forever()
finally:
    logger.info('Shutting down...')
    picam2.stop_recording()
    video_writer.close()
    logger.info('Shutdown complete')
