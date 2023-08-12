#!/bin/sh
cd /home/pi/mjpg-streamer/mjpg-streamer-experimental/
mjpg_streamer -o './output_http.so -w ./www -p 8080' -i './input_raspicam.so -x 1920 -y 1080 -fps 30 -q 10'D &
