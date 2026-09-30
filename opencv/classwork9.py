import cv2
img = cv2.imread('lena02.png')
rows, cols = img.shape[:2]
center = (cols / 2, rows / 2)
M = cv2.getRotationMatrix2D(center, 30, 0.6)
dst = cv2.warpAffine(img, M, (cols, rows))
cv2.imshow('original', img)
cv2.imshow('rotated (30 deg ccw, scale=0.6)', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
