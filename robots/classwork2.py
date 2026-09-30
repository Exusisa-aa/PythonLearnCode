import re
import pandas as pd
pd.set_option('display.unicode.east_asian_width', True)

text1 = "15240242  445222199512064339 137 1425 5378 0755-26532659        23451234@qq.com"
text2 = "15240243  430581199611267377 13040808478 (0575)2347223          yjf@szpt.edu.cm"
text3 = "15240244  440306199710140217 15920099243 26731415                 wangfuquan@163.com"
text4 = "15240245  445281199508191116 13714255059 2654-1398               wudada@szu.edu.com"
text5 = "15240246  440301199709158012 13147066862 010 48624865           jinfeng@tom.com"
text6 = "15240247  44030319950121812X 13665560541 8016-5984               kufula@126.com"

# 各类信息的正则表达式
EMP_PATTERN = r'\d{8}'                          # 工号：8位数字
ID_PATTERN = r'\d{17}[\dXx]'                    # 身份证：17位数字 + 数字或X
MOBILE_PATTERN = r'1[3-9]\d(?:[ -]?\d{4}){2}'   # 手机：1[3-9]开头共11位，数字间可有空格/短横
LANDLINE_PATTERN = r'(?:\(?0\d{2,3}\)?[-\s]?\d{7,8}|\d{3,4}-\d{4}|\d{7,8})'  # 固定电话
EMAIL_PATTERN = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'            # 邮箱

rows = []
for text in [text1, text2, text3, text4, text5, text6]:
    # 工号：开头 8 位数字
    emp_id = re.match(EMP_PATTERN, text).group()

    # 身份证：18 位（17 位数字 + 数字或 X）
    m_id = re.search(ID_PATTERN, text)
    id_card = m_id.group()

    # 手机：在身份证之后查找（避免误匹配身份证内部的数字），并去掉数字间的空格/短横
    m_mobile = re.search(MOBILE_PATTERN, text[m_id.end():])
    mobile = re.sub(r'[ -]', '', m_mobile.group())

    # 邮箱
    m_email = re.search(EMAIL_PATTERN, text)
    email = m_email.group()

    # 固定电话：位于手机之后、邮箱之前
    between = text[m_id.end() + m_mobile.end():m_email.start()]
    landline = re.search(LANDLINE_PATTERN, between).group()

    rows.append([emp_id, id_card, mobile, landline, email])

df = pd.DataFrame(rows, columns=['工号', '身份证', '手机', '固定电话', '邮箱'])
print(df)