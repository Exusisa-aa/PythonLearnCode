output = open("file.txt", "w")
output.write("这是最新的输入")
output.close()

output = open("file.txt", "a")
output.write("这是追加的信息！")
output.close()

file = open("file.txt", "r")
for line in file:
    print(line)
file.close()