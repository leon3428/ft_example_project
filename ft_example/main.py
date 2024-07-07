from lib.controller import *
from lib.display import *
import cv2

recording = False
stop = False

def on_button_clicked(event):
    global recording
    global stop

    if recording:
        stop = True
    else:
        recording = True
        display.set_attr("record.text", "stop")

display.button_clicked("record", on_button_clicked)
 
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
out = cv2.VideoWriter('/opt/ft/outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))
 
while(True):
    ret, frame = cap.read()

    if recording:
        out.write(frame)
    if stop:
        break

cap.release()
out.release()