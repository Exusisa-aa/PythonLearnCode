a = 1
b = 2
c = 3
if (c > b) and (a > c):
    print("c大于b")
elif a > c:
    print("a大于c")
else:
    print("b大于c")
print("----------------------------------------------------------------")
f = 10
g = 1
while g < f:
    print(g)
    g += 1
else:
    print("循环正常结束")
print("----------------------------------------------------------------")
h = [11, 12, 13, 14, 15]
for i in h:
    print(i)
else:
    print("循环正常结束")
print("----------------------------------------------------------------")
d = input("输入数字:")
match d:
    case "1":
        print("你输入的是1")
    case "2" if isinstance(d,str):
        print("你输入的是2")
    case "3" | "4":
        print("你输入的是3或4")
    case _:
        print("你输入的数字不在1-3之间")
print("----------------------------------------------------------------")
m = input("请输入长:")
n = input("请输入宽:")
for i in range(int(n)):
    for j in range(int(m)):
        print("*",end=" ") #end表示以什么结束，默认为\n表示换行，若不想换行则换为空
    print("")