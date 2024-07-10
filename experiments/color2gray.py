import cv2
import numpy as np

img = cv2.imread('assets/img.png')

gray1 = np.mean(img, axis=2)
cv2.imwrite('avg.png', gray1)

gray2 = 0.114 * img[:,:,0] + 0.587 * img[:,:,1] + 0.299 * img[:,:,2]
cv2.imwrite('weighted.png', gray2)