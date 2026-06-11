import random

for i in range(1,10):
    for j in range(1,i+1):
        if j == 5 :
            break
        print(f"{j} x {i} = {j*i}",end="\t")
    print("")
print("-------------------------------------------------------------")
rNum = random.randint(1,100)
while True:
    num = input("请输入数字：")
    if int(num) > rNum :
        print("太大了")
    elif int(num) < rNum :
        print("太小了")
    else:
        print("恭喜你猜对了,",end="")
        break
print(f"该数字为{rNum}")