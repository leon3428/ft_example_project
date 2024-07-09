import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

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

def main():
    cap = cv2.VideoCapture('assets/out2.avi')

    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    detection_line = 380
    offset = 20

    avg = 320

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        height, width, _ = frame.shape

        middle = find_lane_center(frame, detection_line, offset)
        avg = avg * 0.8 + middle * 0.2

        cv2.line(frame, (0, detection_line), (width, detection_line), (255, 0, 0), 5)
        cv2.circle(frame, (int(avg), detection_line), 20, (0, 255, 0), -1)
        cv2.imshow('Frame', frame)

        if cv2.waitKey(75) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()