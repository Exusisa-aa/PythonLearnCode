import cv2
img = cv2.imread('lena02.png')
print("原图 shape (高, 宽, 通道):", img.shape)
dst = cv2.resize(img, (224, 224))
print("压缩后 shape (高, 宽, 通道):", dst.shape)
cv2.imshow('original (512x512)', img)
cv2.imshow('resized (224x224)', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
