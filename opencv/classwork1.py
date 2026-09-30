import cv2
import matplotlib.pyplot as plt

img_plt = plt.imread('lena02.png')                    # 读取图像 (float32, RGB)
img_plt = cv2.cvtColor(img_plt, cv2.COLOR_RGB2BGR)    # 色彩空间转换 RGB -> BGR
img_plt = (img_plt * 255).astype('uint8')             # 值域缩放 float[0,1] -> uint8[0,255]
cv2.imshow('matplotlib imread (RGB2BGR)', img_plt)    # 显示图像

# 2. 用 opencv-python 的 imread 读取 lena02，并显示灰度图像
img = cv2.imread('lena02.png')                        # 读取图像 (uint8, BGR)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)          # 色彩空间转换 BGR -> GRAY
cv2.imshow('opencv imread (BGR2GRAY)', gray)          # 显示图像

cv2.waitKey(0)
cv2.destroyAllWindows()
