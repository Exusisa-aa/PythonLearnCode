import cv2
lena = cv2.imread("lena03.png")
logo = cv2.imread("opencv-logo.png")
h, w = logo.shape[:2]
lh, lw = lena.shape[:2]
roi = lena[lh - h:lh, lw - w:lw]
gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
ret1, mask1 = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
cv2.imshow("mask1(抛弃前景掩码)", mask1)
fg1 = cv2.bitwise_and(roi, roi, mask=mask1)
cv2.imshow("fg1(背景局部图)", fg1)
ret2, mask2 = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
cv2.imshow("mask2(保留前景掩码)", mask2)
fg2 = cv2.bitwise_and(logo, logo, mask=mask2)
cv2.imshow("fg2(logo前景局部图)", fg2)
result_roi = cv2.add(fg1, fg2)
lena[lh - h:lh, lw - w:lw] = result_roi
cv2.imshow("最终效果图", lena)
cv2.waitKey(0)
cv2.destroyAllWindows()