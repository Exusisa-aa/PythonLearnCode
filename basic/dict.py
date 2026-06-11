d = {"张三":10,"李四":20,"王五":30,"赵六":40,"孙七":50}
print(d)
print(d["王五"])
d["王五"] = 60
print(d)
print("-------------------------------------------")
d["周八"] = 70
print(d)
d.pop("周八")
del d["赵六"]
print(d)

print(d.get("张三"))
print(d.keys())
print(d.values())
print(d.items())

for key in d:
    print(key,d[key])

for k,v in d.items():
    print(k,v)