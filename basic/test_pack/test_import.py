__all__ = ["add","mul"]
def add(x,y):
    return x+y
def sub(x,y):
    return x-y
def mul(x,y):
    return x*y
def div(x,y):
    return x/y
def print_line():
    print("--------------------------------------------------")

if __name__ == "__main__":
    print(add(20,30))
    print(sub(20,30))
    print(mul(20,30))
    print(div(20,30))