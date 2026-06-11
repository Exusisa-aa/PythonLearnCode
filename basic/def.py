def outline():
    print("--------------------------------------------------")
    return True

def print_dict(dd:dict={"a":1,"b":2,"c":3,"d":4,"e":5}):
    """
    用于遍历字典的方法
    :param dd: 字典名
    :return: 无意义
    """
    for k,v in dd.items():
        print(k,v)
    return True


print(outline())
d = {"张三":10,"李四":20,"王五":30,"赵六":40,"孙七":50}
print_dict(d)


def print_number(n:int=20):
    """
    打印数字
    :param n:数字
    :return: 无意义
    """
    print(n)
    return True

print_number()
print_number(20000)

#不定长参数
def test_args(*args,**kwargs):
    print(args) #元组
    print(kwargs) #字典

test_args(1,2,3,4,5,name="张三",age=20)

