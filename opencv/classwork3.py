import cv2
import numpy as np

# 读取 lena02（cv2 读入为 BGR 顺序）
img = cv2.imread('lena02.png')
print("图像形状:", img.shape)

# 分离三个通道（均为单通道灰度图）
b, g, r = cv2.split(img)

# 将每个通道构造成「只保留该通道、其余置 0」的三通道图，从而以对应颜色显示
# 蓝色通道 -> 只有蓝色分量
b_colored = cv2.merge([b, np.zeros_like(b), np.zeros_like(b)])
# 绿色通道 -> 只有绿色分量
g_colored = cv2.merge([np.zeros_like(g), g, np.zeros_like(g)])
# 红色通道 -> 只有红色分量
r_colored = cv2.merge([np.zeros_like(r), np.zeros_like(r), r])

# 显示
cv2.imshow('Blue  channel', b_colored)
cv2.imshow('Green channel', g_colored)
cv2.imshow('Red   channel', r_colored)

cv2.waitKey(0)
cv2.destroyAllWindows()
