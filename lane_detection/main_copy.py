import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def main():
    matplotlib.use('TKAgg')

    img = cv2.imread('assets/frame2.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    blur = cv2.GaussianBlur(gray, (15,15), 0)

    height, width, _ = img.shape

    detection_line = 380
    offset = 20
    cv2.line(img, (0, detection_line), (width, detection_line), (255, 0, 0), 5)

    line_intensity = blur[detection_line - offset : detection_line + offset, :]
    line_intensity = np.mean(line_intensity, axis=0)
    gradient = np.gradient(line_intensity)
    print(gradient[width//2:].shape)

    right = np.argmin(gradient[ width // 2 : ]) + width // 2
    left = np.argmax(gradient[ : width // 2 ])
    middle = (left + right) // 2

    print(left, right, middle)

    cv2.circle(img, (middle, detection_line), 20, (0, 255, 0), -1)

    print(line_intensity.shape)
    x = list(range(width))
    # plt.plot(x, line_intensity)
    plt.plot(x, gradient)
    plt.show()

    cv2.imshow('window', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()