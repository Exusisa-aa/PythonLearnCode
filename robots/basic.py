import requests
from lxml import html


res = requests.request("GET","https://www.tiobe.com/tiobe-index/")
document = html.fromstring(res.text)

th_list = document.xpath("//table[@id='top20']/thead/tr/th/text()")
td_list = document.xpath("//table[@id='top20']/tbody/tr")


print(th_list)
for tr in td_list:
    tr_data = tr.xpath("./td/text()")
    print(tr_data)

print("---------------------------------------------------------------------------------")
print(document.xpath("//table[@id='top20']/tbody/tr[1]/*/text()"))
print("---------------------------------------------------------------------------------")
print(document.xpath("//a/@href"))



