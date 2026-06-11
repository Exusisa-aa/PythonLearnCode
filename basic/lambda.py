add = lambda x,y : x+y
print_line = lambda : print("--------------------------------------------------")

print(add(20, 30))
print_line()

list0 = ['a','awfnawikfaw','faefae','faegmnaig','faef','fnsikngeiksgnisengiks','dd']
list0.sort(key = lambda item : len(item))
print(list0)