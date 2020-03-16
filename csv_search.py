# -*- coding: utf-8 -*-
import csv
import os

class S1Search(object):
    def __init__(self, path):
        self.path = path
    
    def read(self, word):
        filelist = os.listdir(self.path)
        for f in filelist:
            temp_path = os.path.join(self.path, f)
            f_postfix = os.path.split(f)[-1][-3:]
            if f_postfix == 'csv':
                with open(temp_path, 'r', encoding = 'utf-8-sig') as fd:
                    reader = csv.reader(fd)
                    for row in reader:
                        if word in row[5]:
                            print(f)
                            print(row[20], row[19], row[21])
                            print('*'*100)

path = r'E:\Temp\xls'
word = '该帖被管理员或版主屏蔽'
s1s = S1Search(path)
s1s.read(word)
