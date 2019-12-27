import os
import re
import csv
import getpass
import requests
from html.parser import *

filepath = os.getcwd()
state = []
x = []


class Scraper(HTMLParser):
    def handle_starttag(self, tag, attrs):
        '''
        if tag == 'img':  # 验证码
            attrs = dict(attrs)
            if(attrs.__contains__('id')):
                x.append(attrs['src'])
        '''
        if tag == 'input':  # viewstate
            attrs = dict(attrs)
            if attrs.__contains__('name'):
                if attrs['name'] == '__VIEWSTATE':
                    state.append(attrs['value'])


url = "http://jwxt2.jit.edu.cn/"
webpage = requests.get(url)
Cookie = webpage.cookies
date = webpage.text
parser = Scraper()
parser.feed(date)

Headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
}
print("Note:为了保护隐私，输入密码时不显示字符，并不是程序卡死，正常输入即可")
while(True):
    username = input("输入用户名:")
    password = getpass.getpass('输入密码:')

    url = "http://jwxt2.jit.edu.cn/CheckCode.aspx"  # 验证码
    codePath = filepath+"\\CheckCode.jpg"
    pic = requests.get(url, cookies=Cookie, headers=Headers)
    if os.path.exists(codePath):
        os.remove(codePath)
    with open(codePath, 'wb')as f:
        f.write(pic.content)
        f.close()
    os.startfile(codePath)
    CheckCode = input("输入弹出的验证码:")
    os.remove(codePath)
    payload = {
        '__VIEWSTATE': state[0],
        '__VIEWSTATEGENERATOR': 92719903,
        'txtUserName': username,
        'Textbox1': '',
        'TextBox2': password,
        'txtSecretCode': CheckCode,
        'RadioButtonList1': '%D1%A7%C9%FA',
        'Button1': '',
        'lbLanguage': '',
        'hidPdrs': '',
        'hidsc': '',
    }
    Login = r'http://jwxt2.jit.edu.cn'
    page = requests.post(url=Login, data=payload,
                         headers=Headers, cookies=Cookie)
    title = r'<title>(.*?)</title>'
    x = re.findall(title, page.text)
    if x[0] == "欢迎使用正方教务管理系统！请登录":
        print("登录失败!")
        albert = "defer>alert\('(.*?)'\)|alert\('(.*?)'\)"
        err = re.findall(albert, page.text)
        if err[0][0] == '':
            print(err[0][1])
        else:
            print(err[0][0])

    else:
        print("登录成功!")
        regular = r'<span id="xhxm">(.*?)</span>'
        name = re.findall(regular, page.text)
        name = name[0]
        print("欢迎你:%s" % name)
        break

# 名字编码转换
name = name[:-2]
name = str(name).encode('gb2312')
name = str(name).replace(r'\x', '%')
name = name.upper()[2:]
name = name[:-1]

# 获取成绩信息
lheaders = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Referer': "http://jwxt2.jit.edu.cn/xscj_gc.aspx?xh="+username+"&xm="+name+"&gnmkdm=N121605"
}

lurl = "http://jwxt2.jit.edu.cn/xscj_gc.aspx?xh=" + \
    username+"&xm="+name+"&gnmkdm=N121605"


# 获取__VIEWSTATE
page = requests.get(lurl, cookies=Cookie, headers=lheaders)
parser = Scraper()
parser.feed(page.text)

# 获取学期学年
regular_xn = r'\"\d{4}-\d{4}\"'
result_xn = re.findall(regular_xn, page.text)
for i in range(len(result_xn)):
    result_xn[i] = re.sub("\"", "", result_xn[i])

regular_xq = r'>\d</option>'
result_xq = re.findall(regular_xq, page.text)
for i in range(len(result_xq)):
    result_xq[i] = re.sub("\D", "", result_xq[i])

print("当前可查询的学年:")
for i in range(len(result_xn)):
    print("[%s]:" % (i+1), end="")
    print(result_xn[i])
print("当前可查询的学期:")
for i in range(len(result_xq)):
    print("[%s]:" % (i+1), end="")
    print(result_xq[i])

# 输入学期学年
print("要查询所有成绩,提示输入学年学期时请不要输入，直接回车")
xn = input("输入你要查询的学年前面对应的编号:")
xq = input("输入你要查询的学期前面对应的编号:")
if xn != '':
    xn = result_xn[int(xn)-1]

if xq != '':
    xq = result_xq[int(xq)-1]


payload = {
    '__VIEWSTATE': state[1],
    '__VIEWSTATEGENERATOR': 'DB0F94E3',
    'ddlXN': xn,
    'ddlXQ': xq,
    'Button1': '按学期查询'
}
page = requests.post(lurl, data=payload, headers=lheaders, cookies=Cookie)

# 最后处理成绩信息
regular = r'<td>(.*?)</td>'*16

result = re.findall(regular, re.sub(">&nbsp;<|>0<", "><", page.text))
xm = result[0]  # 项目分离
forma = []
csvPath = filepath+"\\score.csv"
csvfile = open(csvPath, 'w', newline='', encoding='gb2312')
writer = csv.writer(csvfile)
temp = ''
for i in range(16):
    forma.append('')  # 16位的数据存放处理好的数据
for index in range(16):
    for item in result:
        temp = format("% -15s" % str(item[index]).strip())
        forma[index] += temp

'''
for each in forma:
    print(each)
'''

for item in result:
    writer.writerow(item)
csvfile.close()
input("处理完成，成绩结果在运行本程序路径下的score.csv中，按任意键退出")
