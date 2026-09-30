import cv2
import numpy as np
img = cv2.imread('lena02.png')
rows, cols = img.shape[:2]     
tx, ty = 50, 50
M = np.float32([[1, 0, tx],
                [0, 1, ty]])
dst = cv2.warpAffine(img, M, (cols, rows), borderValue=(255, 255, 255))
cv2.imshow('original', img)
cv2.imshow('translated (tx=50, ty=50)', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
