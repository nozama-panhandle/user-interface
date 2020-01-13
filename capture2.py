from streamer import Streamer
import cv2

streamer=Streamer(8888)
server="http://rpi-6.wifi.local.cmu.edu:8888/video_feed"
VCap=cv2.VideoCapture(server)
if not VCap.isOpened():
    print("ERROR! Check the camera.")
    exit(0)
while True:
    ret, frame=VCap.read()
    #if frame==None: continue
    streamer.update_frame(frame)

    if not streamer.is_streaming:
        streamer.start_streaming()
    cv2.waitKey(10)
