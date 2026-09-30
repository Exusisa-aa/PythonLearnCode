import cv2
import numpy as np
img = cv2.imread('lena02.png')
def gamma_correct(img, gamma):
    img_norm = img / 255.0                 
    cor_img = np.power(img_norm, gamma)     
    return np.clip(cor_img * 255, 0, 255).astype('uint8')   
cor_img_05 = gamma_correct(img, 0.5)
cor_img_22 = gamma_correct(img, 2.2)
cv2.imshow('original', img)
cv2.imshow('gamma = 0.5 (lighter)', cor_img_05)
cv2.imshow('gamma = 2.2 (darker)', cor_img_22)
cv2.waitKey(0)
cv2.destroyAllWindows()
