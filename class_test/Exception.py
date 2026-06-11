try:
    print(1/0)
    #print(a)
except ZeroDivisionError as e:
    print(e)
except NameError as e:
    print(e)
except Exception as e:
    print(e)
finally:
    print("程序结束")