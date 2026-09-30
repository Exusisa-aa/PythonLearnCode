import cv2
img = cv2.imread('lena02.png')
print("原图 shape (高, 宽, 通道):", img.shape)
dst = cv2.resize(img, None, fx=0.5, fy=0.6)
print("缩放后 shape (高, 宽, 通道):", dst.shape)
cv2.imshow('original (512x512)', img)
cv2.imshow('resized (fx=0.5, fy=0.6)', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
