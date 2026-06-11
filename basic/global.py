num = 100


def change():
    """
    测试全局变量
    :return: 无
    """
    global num
    num = 10000
    print(num)
    return True


print(num)
change()
print(num)