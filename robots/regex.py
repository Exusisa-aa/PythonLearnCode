import re

s1 = "15384238051,13602333144，滋滋滋滋滋滋滋滋"
s2 = "滋滋滋滋滋滋滋滋，15384238051,13602333144,8217480912740817048712,147808"

#match：匹配字符串的开头部分，只返回一个匹配结果，并且匹配结果需要通过group()函数获取
result1 = re.match("1[3-9]\\d{9}",s1)
print(result1.group())
print(result1.span())
print(result1.start())
print(result1.end())
print("=================================================")
#search：匹配字符串的任意位置，只返回一个匹配结果，并且匹配结果需要通过group()函数获取
result2 = re.search("1[3-9]\\d{9}",s2)
print(result2.group())
print("=================================================")
#search：匹配字符串的任意位置，返回所有匹配结果，并且匹配结果不需要需要通过group()函数获取
result3 = re.findall("1[3-9]\\d{9}",s2)
print(result3)