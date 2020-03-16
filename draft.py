#-*- coding: utf-8 -*-
import requests
from lxml import etree
from urllib import parse
from PyQt5.QtWidgets import (QWidget, QPushButton,
    QFrame, QApplication)
from PyQt5.QtGui import QColor
# import numpy
# import cv2
import sys
# from PIL import Image
import time, random
import datetime
import re,os, json, traceback
from functools import wraps, partial, update_wrapper
from collections import OrderedDict
from time import sleep


# for id in range(1552162,1552164):
#     str = 'https://bbs.saraba1st.com/2b/thread-{id}-1-1.html'
#     address = str.format_map(vars())
#     print(address)

headers = {
    'user-agent':  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
}
# name = input('please enter ur username')
# pswd = input('please enter ur password')
data = {
    'username':'DJI',
    'password':'s1gongchehao@',
}
url = r'https://bbs.saraba1st.com/2b/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
sessions = requests.Session()
sessions.post(url,data=data, headers = headers)
# str1 = r'https://bbs.saraba1st.com/2b/thread-1729918-1-1.html' # 观测站
# str1 = r'https://bbs.saraba1st.com/2b/thread-1911758-2-1.html' # S1专楼下载器
# str1 = r'https://bbs.saraba1st.com/2b/thread-1911165-1-1.html' # 游戏区
# str1 = r'https://bbs.saraba1st.com/2b/thread-1915557-14-1.html' # S1 VTB
str1 = r'https://bbs.saraba1st.com/2b/thread-765782-1-1.html'
h = sessions.get(str1, headers = headers)
root = etree.HTML(h.text)
s = h.text
# pstmsgid = 19499
pstmsgid = 17213815
# pstmsgid = 46486702

# today=datetime.date.today()
# print(today)

# path=r'C:\Users\Oval Liu\Desktop\douban.txt'
# with open(path,"w",encoding='utf-8') as f:
#     f.write(s)


def deal_garbled(info):
    """处理乱码"""
    info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
        sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
    return info

config_path = os.path.split(
        os.path.realpath(__file__))[0] + os.sep + 'config.json'

postmsg_xpath = '//*[@id="pid17213815"]/tr[1]/td[2]/div[2]/div/div'
score = root.xpath(postmsg_xpath)[0].text
print(score)

# post = deal_garbled(post)
# # print(post)
# q_pattern_3 = r'引用第(\d+)楼(.*)于(\d{4}-(\d+)-(\d+)(\s)(\d+):(\d+))发表的(\s+):'
# if re.search(q_pattern_3, post):
#     print(re.findall(q_pattern_3, post))


# print(text)
# with open(config_path) as f:
#     config = json.loads(f.read())

#     if type(config['thread_id_list']) == type(u""):
#         user_id_list = config['thread_id_list']
#         if not os.path.isabs(user_id_list):
#             user_id_list = os.path.split(
#                 os.path.realpath(__file__))[0] + os.sep + user_id_list
#         with open(config['thread_id_list'], 'rb') as f:
#             lines = f.read().splitlines()
#             lines = [line.decode('utf-8') for line in lines]
#             config['thread_id_list'] = [
#                 line.split(' ')[0] for line in lines if
#                 len(line.split(' ')) > 0 and line.split(' ')[0].isdigit()
#             ]
#     elif config['thread_id_list'] == 1:
#         config['thread_id_list'] = range(1916495, 1916497)

    # for id_ in config['thread_id_list']:
    #     print(id_)



class Integer:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError('Expected an int')
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]

class Point:
    x = Integer('x')
    y = Integer('y')

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def test(self):
        return type(self)

# print(Point(2, 3).test)
# print(Integer(123).__get__(123, None))
# p = Point(2, 3)
# # del p.x
# print(p.__dict__, p.x)

# test = root.xpath('//*[@id="favatar46281431"]/p[1]/em/a')
# print(test[0].text)

def make_xlat(*args, **kwds):  
    adict = dict(*args, **kwds)  
    rx = re.compile('|'.join(map(re.escape, adict)))  
    def one_xlat(match):  
        return adict[match.group(0)]  
    def xlat(text):  
        return rx.sub(one_xlat, text)  
    return xlat 

adict = {  
    '<font+(.*?)>' : '',  
    '</font>' : '',  
    '<strong>' : '', 
    '</strong>' : '',  
}  

# translate = make_xlat(adict)  
# print(re.compile('|'.join(map(str, adict)) ))
# print(re.compile('<strong>').group(0))
# print(translate(h.text))

# font_rule1 = re.compile(r'<font+(.*?)>|</font>|<strong>|</strong>')
# s = re.sub(font_rule1, '', h.text)

# # urlencode
# str = '77f64fe8b40fad28cb3c835b43916fd0'
# str2 = parse.unquote(str)
# print(str2)

# class S1(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.initUI()
#
#     def initUI(self):
#         self.col = QColor(0, 0, 0)
#
#         # self.square = QFrame(self)
#         # self.square.setGeometry(150, 20, 100, 100)
#         # self.square.setStyleSheet("QWidget { background-color: %s }" %
#         #                           self.col.name())
#
#         self.setGeometry(300, 300, 280, 170)
#         self.setWindowTitle('Toggle button')x
#         self.show()
#
# if __name__ == '__main__':
#
#     app = QApplication(sys.argv)
#     ex = S1()
#     sys.exit(app.exec_())

# cap = cv2.VideoCapture(0)
# starttime = time.perf_counter_ns()
# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#     endtime = time.perf_counter_ns()
#     if cv2.waitKey(1)&endtime-starttime>=2045260798:
#         cv2.imwrite(r'C:\Users\Oval Liu\Desktop\excuse.png',frame)
#         break
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()