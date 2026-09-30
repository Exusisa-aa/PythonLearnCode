import cv2
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
img = cv2.imread('lena02.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
dst = cv2.equalizeHist(gray)
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.hist(gray.ravel(), bins=256, range=(0, 256))
plt.title("原图直方图")
plt.subplot(1, 2, 2)
plt.hist(dst.ravel(), bins=256, range=(0, 256))
plt.title("均衡化直方图")
plt.show()
cv2.imshow('gray (原灰度图)', gray)
cv2.imshow('equalized (均衡化后)', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
