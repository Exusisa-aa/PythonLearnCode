s = {1,2,2,3,3,5,6,9,88,88} #无序无索引不重复
print(s)
s.add(10)
print(s)
s.remove(10)
print(s)
s.pop()
print(s)
a = {i**2 for i in s if i % 2 == 0}
s.clear()
print(s)
print(a)