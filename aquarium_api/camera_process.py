#!/usr/bin/env python3
"""Standalone camera process that serves MJPEG at /stream.mjpg on localhost:8010.

Run this as a service (systemd) so the camera is always managed by a single
process and does not get reinitialized on client reconnects.
"""
import io
import logging
import socketserver
from http import server
from threading import Condition

try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
except Exception as e:
    Picamera2 = None
    JpegEncoder = None
    FileOutput = None
    logging.exception("picamera2 import failed: %s", e)

PAGE = """\
<html>
<head>
<title>Camera server</title>
</head>
<body>
<h1>Camera server</h1>
<img src="/stream.mjpg" width="640" height="480" />
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def writable(self):
        return True

    def write(self, buf):
        with self.condition:
            self.frame = bytes(buf)
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
            if Picamera2 is None:
                self.send_error(500, 'picamera2 not available')
                return
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
                    if frame is None:
                        continue
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, e)
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def run_server(host='127.0.0.1', port=8010, width=640, height=480):
    global output
    output = StreamingOutput()

    if Picamera2 is None:
        logging.error('picamera2 not available; exiting')
        return

    picam2 = Picamera2()
    try:
        picam2.configure(picam2.create_video_configuration(main={'size': (width, height)}))
        encoder = JpegEncoder()
        picam2.start_recording(encoder, FileOutput(output))
    except Exception:
        logging.exception('Failed to start camera')
        return

    try:
        address = (host, port)
        server = StreamingServer(address, StreamingHandler)
        logging.info('Camera server running on http://%s:%d', host, port)
        server.serve_forever()
    finally:
        try:
            picam2.stop_recording()
        except Exception:
            pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_server()
