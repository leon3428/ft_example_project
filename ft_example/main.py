from lib.controller import *
from lib.display import *
from fischertechnik.controller.Motor import Motor
import cv2
import numpy as np

def find_lane_center(frame, detection_line, offset):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    blur = cv2.GaussianBlur(gray, (15,15), 0)

    height, width, _ = frame.shape
    detection_line = 380
    offset = 20

    line_intensity = blur[detection_line - offset : detection_line + offset, :]
    line_intensity = np.mean(line_intensity, axis=0)
    gradient = np.gradient(line_intensity)

    right = np.argmin(gradient[ width // 2 : ]) + width // 2
    left = np.argmax(gradient[ : width // 2 ])
    middle = (left + right) // 2

    return middle

class PID:
    def __init__(self, target, kp) -> None:
        self.target = target
        self.kp = kp

    def update(self, value):
        error = value - self.target
        return error * self.kp

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    detection_line = 380
    offset = 20

    avg = 320

    pid = PID(290, -0.5)
    motor.set_speed(160, Motor.CW)
    motor.start_sync()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        middle = find_lane_center(frame, detection_line, offset)
        avg = avg * 0.8 + middle * 0.2
        value = pid.update(avg)
        value += 256
        value = min(value, 306)
        value = max(value, 206)

        print(value)
        servo.set_position(int(value))
        
    cap.release()


if __name__ == '__main__':
    main()