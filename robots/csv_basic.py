import csv
import requests
from lxml import html

res = requests.request("GET","https://www.tiobe.com/tiobe-index/")  #获取网页源代码
document = html.fromstring(res.text) #解析网页源代码为HTML对象

#头列表的写入传列表，数据的写入传字典
with open("csv_data/csv_data_01.csv","w",encoding="UTF-8",newline="") as f: #创建csv文件并指定文件对象，w为写模式，UTF-8为编码格式，newline为换行符，\n为换行符
    header = document.xpath("//table[@id='top20']/thead/tr/th/text()") #获取表头列表
    writer = csv.DictWriter(f,fieldnames=header) #创建操作的csv文件对象，并指定文件对象和表头列表
    writer.writeheader() #写入表头

    tr_list = document.xpath("//table[@id='top20']/tbody/tr") #获取数据列表的每一行的对象的列表
    for tr in tr_list:
        tr_data = tr.xpath("./td/text()") #获取数据列表的每一行数据的列表
        writer.writerow(dict(zip(header,tr_data))) #将数据写入csv文件，zip()函数将头列表和数据列表组合成一一对应的元组，dict()函数将元组转换为字典

with open("csv_data/csv_data_01.csv","r",encoding="UTF-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)
