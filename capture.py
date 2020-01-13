import cv2

server="http://rpi-6.wifi.local.cmu.edu:8888/video_feed"
VCap=cv2.VideoCapture(server)
if not VCap.isOpened():
    print("ERROR!")
for i in range(1):
    ret, frame=VCap.read()
    cv2.imwrite("frame.jpg", frame)
