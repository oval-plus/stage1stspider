# -*- coding: utf-8 -*-

import requests
from lxml import etree
import re, sys, os
from tqdm import tqdm
import random
from time import sleep
from collections import OrderedDict

from html_parser import Stage1stParser
from Writer import Writer, write_log

class Spider(object):
    def __init__(self, config):
        self.config = config
        self.merge_mode = self.config['merge_mode']
        self.flag = 0
        self.slice_num = self.config['slice_num']
        try:
            if type(config['thread_id_list']) == type(u""): # "thread_id.txt"
                thread_id_list = config['thread_id_list']
                if not os.path.isabs(thread_id_list):
                    thread_id_list = os.path.split(
                        os.path.realpath(__file__))[0] + os.sep + thread_id_list
                with open(config['thread_id_list'], 'rb') as f:
                    lines = f.read().splitlines()
                    lines = [line.decode('utf-8') for line in lines]
                    config['thread_id_list'] = [
                        line.split(' ')[0] for line in lines if
                        len(line.split(' ')) > 0 and line.split(' ')[0].isdigit()
                    ]
            elif config['thread_id_list']:
                self.config['thread_id_list'] = range(774061, 1792000)
                
            else:
                raise Exception
        except Exception:
            print('如果想输入帖子id，请到thread_id.txt输入。如果想把整个S1爬下来，请把config.json中thread_id_list的值改为true。')
            sys.exit()

        self.parser = Stage1stParser(self.config)
        self.session = Stage1stParser(self.config).loginSession()

        self.writer = Writer(self.config)

    def csv_automatic_tools(self, thread_info):
        if int(thread_info['thread_id']) % self.slice_num != 0 and self.flag != 0 and (self.merge_mode):
            pass
        else:
            self.writer.write_thread(thread_info)

    def get_one_page(self, page, threadNum, pageNum):
        '''获取第page页的所有帖子'''
        sessions = self.session
        page = self.parser.get_page(sessions, threadNum, pageNum)
        selected_postid = self.parser.get_pstmsgid(page)
        n = len(selected_postid)

        for i in range(0, n):
            floor = self.parser.get_floor(page, selected_postid[i], i)
            
            if selected_postid[i] not in self.pinned_post:
                post = self.parser.get_one_post(page, selected_postid[i])
                post['pid'] = selected_postid[i]
                post['floor'] = floor
                post = OrderedDict({**post, **self.thread_info})

                self.post.append(post)

                self.writer.write_post([post])

            if re.search(r'来自(.*)', str(floor)):
                self.pinned_post.append(selected_postid[i])

    def get_thread_info(self):
        sessions = self.session
        page = self.parser.get_page(sessions, self.thread_info['thread_id'], 1)
        isexist = self.parser.existPost(page)
        if isexist:
            thread = self.parser.get_Index(page)
            page_num = int(thread['pageNum'])
            self.thread_info = {**self.thread_info, **thread} # merge two dicts
            if 'csv' in self.config['write_mode']:
                self.csv_automatic_tools(self.thread_info)
                self.flag = 1
            else:
                self.writer.write_thread(self.thread_info)
                self.flag = 1

            # page1 = 0
            # random_pages = random.randint(1, 3)
            for p in tqdm(range(1, page_num + 1), desc = 'Progress'):
                self.get_one_page(page, self.thread_info['thread_id'], p)

                # if p - page1 == random_pages and p < page_num:
                #     sleep(random.randint(6, 10)) # Stub file for the 'time' module.
                #     page1 = p
                #     random_pages = random.randint(1, 3)
                sleep(3)
            return 'OK'
        else:
            write_log(self.thread_info['thread_id'])
            sleep(1)
            if int(self.thread_info['thread_id']) % self.slice_num == 0:
                self.writer.write_thread(self.thread_info)
                self.flag = 1
            return 'Not Exist'

    def initialize_info(self, thread_id):
        '''初始化爬虫信息'''
        self.thread_info = {'thread_id': thread_id}
        self.post = []
        self.pinned_post = []  

    def start(self):
        '''运行爬虫'''
        for id_ in self.config['thread_id_list']:
            self.initialize_info(id_)
            print('*' * 100)
            print(self.get_thread_info())
            self.pinned_post = []                
            print(u'信息抓取完毕')
            print(self.thread_info['thread_id'])
            print('*' * 100)

if __name__ == '__main__':
    import json
    config_path = os.path.split(
        os.path.realpath(__file__))[0] + os.sep + 'config.json'
    if not os.path.isfile(config_path):
        sys.exit(u'当前路径：%s 不存在配置文件config.json' %
                 (os.path.split(os.path.realpath(__file__))[0] + os.sep))
    with open(config_path, encoding = 'utf-8-sig') as f:
        config = json.loads(f.read())
    spider = Spider(config)
    spider.start()