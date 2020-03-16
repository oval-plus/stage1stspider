# -*- coding: utf-8 -*-

import pymysql
import os, sys
import datetime
import csv

def get_filepath(type, thread_id):
    """获取结果文件路径"""
    today = str(datetime.date.today())
    file_dir = os.path.split(
        os.path.realpath(__file__))[0] + os.sep + 'tiezi' + os.sep + today
    if type == 'img' or type == 'video':
        file_dir = file_dir + os.sep + type
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    if type == 'img' or type == 'video':
        return file_dir
    file_path = file_dir + os.sep + today + '-' + str(thread_id) + '.' + type
    return file_path

def write_log(content):
    today = str(datetime.date.today())
    file_dir = os.path.split(
        os.path.realpath(__file__))[0] + os.sep + 'tiezi' + os.sep + today
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    file_path = file_dir + os.sep + today + '-log.txt'
    content = str(content) + '\n'
    with open(file_path, 'ab') as f:
        f.write(content.encode(sys.stdout.encoding))


class Writer(object):
    def __init__(self, config):
        write_mode = config['write_mode']
        self.writers = []

        if 'txt' in write_mode:
            self.writers.append(TxtWriter(config))
        if 'csv' in write_mode:
            self.writers.append(CsvWriter(config))

    def write_thread(self, thread_info):
        for writer in self.writers:
            writer.write_thread(thread_info)

    def write_post(self, post):
        for writer in self.writers:
            writer.write_post(post)

class TxtWriter(object):
    def __init__(self, config):
        self.config = config

    def write_thread(self, thread_info):
        self.thread_info = thread_info
        result_header = (u'\n\n帖子id：\n' + str(self.thread_info['thread_id']) + '\n'+ 
                        u'帖子信息：\n查看：' + str(self.thread_info['viewNum']) + 
                        u'\n发帖数目：' + str(self.thread_info['postNum']) + 
                        u'\n分区：' + str(self.thread_info['fenqu']) + 
                        u'\n标签：' + str(self.thread_info['tag']) + 
                        u'\n标题：' + str(self.thread_info['subject']) + '\n\n')
        
        with open(get_filepath('txt', self.thread_info['thread_id']), 'ab') as f:
            f.write(result_header.encode(sys.stdout.encoding))

    def write_post(self, post):
        temp_result = []
        for p in post:
            temp_result.append(str(p['floor']) + '\n' + p['post_content'] + '\n' + u'小尾巴：' + p['tail'] + '\n' +
                                u'作者：' + str(p['author']) + ' ' + u'发表时间：' + p['post_time'] + 
                                '\n' + u'战斗力：' + str(p['zhandouli']) + '\n\n')
        result = ''.join(temp_result)

        with open(get_filepath('txt', self.thread_info['thread_id']), 'ab') as f:
            f.write(result.encode(sys.stdout.encoding))
        print(get_filepath('txt', self.thread_info['thread_id']))


class CsvWriter(object):
    def __init__(self, config):
        self.config = config
        self.merge_mode = self.config['merge_mode']
        self.slice_thread = 0
        self.slice_num = 500
        self.flag = 0

    def slide_thread(self, thread_info):
        if not self.merge_mode:
            path = get_filepath('csv', thread_info)
        elif self.flag == 0 and self.config['thread_id_list']:
            path = get_filepath('csv', thread_info)
            self.slice_thread = thread_info
            self.flag += 1
        elif int(thread_info) % self.slice_num == 0 and self.config['thread_id_list']:
            path = get_filepath('csv', thread_info)
            self.slice_thread = thread_info
        elif self.config['thread_id_list']:
            path = get_filepath('csv', self.slice_thread)
        else:
            path = get_filepath('csv', 0)
        return path
        
    def write_thread(self, thread_info):
        self.thread_info = thread_info
        result_headers = [
            'quote_status',
            'tail',
            'bilibili_video',
            'scores',
            'score_people_num',
            'post_content',
            'post_time',
            'edit_status',
            'edit_time',
            'editor',
            'author',
            'author_uid',
            'register_time',
            'points',
            'level',
            'recommend',
            'zhandouli',
            'history_post_num',
            'post_id',
            'floor',
            'thread_id',
            'title',
            'section',
            'view_num',
            'post_num',
            'tag',
            'page_num',
        ]
        path = self.slide_thread(self.thread_info['thread_id'])

        with open(path, 'a', encoding = 'utf-8-sig',
                    newline = '') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows([result_headers])

    def write_post(self, post):
        result_data = [p.values() for p in post]
        
        path = self.slide_thread(self.thread_info['thread_id'])

        with open(path, 'a', encoding = 'utf-8-sig', newline = '') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(result_data)
