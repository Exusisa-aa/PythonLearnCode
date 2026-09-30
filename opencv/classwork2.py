import cv2
import numpy as np

img = cv2.imread('lena02.png')
print("图像形状:", img.shape)

print("第4行39列像素 (索引):", img[4, 39])                          # 索引方式 -> [B, G, R]
print("第4行39列像素 (item):",                                    # item() 方式
      img.item(4, 39, 0), img.item(4, 39, 1), img.item(4, 39, 2))

before = img.copy()                    # 保留修改前图像用于对比
img[3:32, 51:62] = 0                   # 切片修改 ndarray[y0:y1, x0:x1]，改为 0
cv2.imshow('before', before)
cv2.imshow('after', img)

mouth = img.copy()
mouth[348:382, 250:350] = 0            # 切片遮盖嘴巴区域
cv2.imshow('mouth covered', mouth)

img[4, 39] = 255                       # ndarray[] = ***  修改像素值
print("修改后第4行39列像素:", img[4, 39])

cv2.waitKey(0)
cv2.destroyAllWindows()
