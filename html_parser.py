# -*- coding: utf-8 -*-

import requests
from lxml import etree
import re, time, sys, os
import json
import traceback

from time import sleep
from collections import OrderedDict

class try_except(object):
    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, owner):
        self.instance_ = instance
        return self

    def __call__(self, *args, **kwargs):
        try:
            return self.fn(self.instance_, *args, **kwargs)
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

class Stage1stParser(object):
    def __init__(self, config):
        # base链接地址
        self.config = config

    def loginSession(self):
        data = self.config['login_data']
        url = r'https://bbs.saraba1st.com/2b/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        sessions = requests.Session()
        sessions.post(url, data = data, headers = self.config['headers'])
        return sessions

    def get_page(self, sessions, threadNum, pageNum):
        '''获取页面'''
        test_address = self.config['baseUrl'] + str(threadNum) + '-' + str(pageNum) + '-1.html'
        h = sessions.get(test_address, headers = self.config['headers'])
        page = etree.HTML(h.text)
        return page

    def deal_garbled(self, content):
        """处理乱码"""
        content = (content.xpath('string(.)').replace(u'\u200b', '').encode(
            sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
        return content

    def existPost(self, page):
        existPost = page.xpath('//*[@id="messagetext"]')
        if existPost != []:
            return False # Sorry, obey or die.
        else:
            return True 

    def get_Index(self, page):
        info = {}     
        try:   
            info['subject'] = page.xpath("//span[@id = 'thread_subject']")[0].text
            info['fenqu'] = page.xpath('//*[@id="pt"]/div/a[4]')[0].text
            info['viewNum'] = page.xpath('//*[@class="xi1"]')[0].text
            info['postNum'] = page.xpath('//*[@class="xi1"]')[1].text          

            try:
                tag = page.xpath('//*[@class="ts"]/a')[0].text
                info['tag'] = re.findall(r'\[(.*?)\]', tag)[0]
            except IndexError:
                info['tag'] = '无标签'

            try:
                pagenum = page.xpath('//*[@id="pgt"]/div/div/label/span')[0].text
                info['pageNum'] = re.findall(r'\d+', pagenum)[0]
            except IndexError:
                info['pageNum'] = 1
        except Exception as e:
                print('Fail to catch the index info')
                print(e)
                sys.exit()

        return info

    def get_pstmsgid(self, page):
        context = page.xpath('//*[@id="postlist"]//div/@id')
        postid_rule = re.compile(r'post_[0-9]+')
        selected_postid = list(filter(lambda x: re.search(postid_rule, x), context))
        selected_postid = list(map(lambda x: x[5:], selected_postid))
        return selected_postid
        
    def get_post_context(self, page, pstmsgid):
        '''获取一条帖子内容：帖子内容、小尾巴、引用回复、直接插哔哩哔哩视频情况'''
        content = {}
        postmsg_xpath = '//*[@id="postmessage_{pstmsgid}"]'
        postmsg_xpath = postmsg_xpath.format_map(vars())
        try:
            post_content = page.xpath(postmsg_xpath)[0]
            post_content = self.deal_garbled(post_content)
            # 小尾巴
            tail_pattern = '-- 来自 (.*)|— from (.*)|—— 来自 (.*)|——— 来自Stage1st(.*)|----发送自 (.*)|—— from (.*)|−−− post by(.*)'
            # 引用回复
            quote_list = []
            quote = page.xpath('//*[@id="postmessage_{pstmsgid}"]/div[@class="quote"]/blockquote'.format_map(vars()))
            if quote == []:
                quote_status = False
            else:
                for q in quote:
                    quote_trans = self.deal_garbled(q)
                    quote_list.append(quote_trans)

                q_pattern_1 = r'(.*)发表于(\s)(\d{4}-(\d+)-(\d+)(\s)(\d+):(\d+))'
                q_pattern_2 = r'最初由(.*)发布(\r\n)(\[)B(\])([\s\S]*)(\[)(\/)B(\])'
                q_pattern_3 = r'引用第(\d+)楼(.*)于(\d{4}-(\d+)-(\d+)(\s)(\d+):(\d+))发表的(\s+)'
                for q_name in quote_list:
                    if re.search(q_pattern_1, q_name):
                        post_content = post_content.replace(q_name, '')
                    elif re.search(q_pattern_2, q_name):
                        post_content = post_content.replace(q_name, '')
                    elif re.search(q_pattern_3, q_name):
                        post_content = post_content.replace(q_name, '')
                quote_status = True
                    # q_pid_xpath = '//*[@id="postmessage_{pstmsgid}"]/div[@class="quote"]/blockquote/font/a/@href'
                    # quote_pid = page.xpath(q_pid_xpath.format_map(vars()))[0]
                    # quote_pid = re.findall(r'pid=(\d+)', quote_pid)[0] # 被回复的帖子
                
            content['quote_status'] = quote_status
            
            # 小尾巴情况    
            tail = re.findall(tail_pattern, post_content)
            if tail == []:
                content['tail'] = False
            else:
                content['tail'] = list(filter(None, tail[0]))[0]
            # 处理编辑条目
            if self.get_edit_status(page, pstmsgid):
                edit_pattern = r'\r\n\s本帖最后由(.*)于(.*)编辑'
                post_content = re.sub(edit_pattern, '', post_content)
            # 比比汗丽丽视频
            b_video = page.xpath('//*[@id="postmessage_{pstmsgid}"]/iframe')
            if b_video != []:
                content['bilibili_heimu'] = True
            else:
                content['bilibili_heimu'] = False
            # 引用代码 
            blockcode_xpath = page.xpath('//*[@id="postmessage_{pstmsgid}"]/div[@class="blockcode"]'.format_map(vars()))
            if blockcode_xpath != []:
                blockcode_pattern = r'复制代码'
                post_content = re.sub(blockcode_pattern, '', post_content)
            # 附件问题
            img_attach = r'\r\n(.*)(\.)(.*) (\((.*)B, 下载次数: (\d+)\))\r\n\r\n下载附件\r\n\r\n\r\n\r\n(\d{4}-(\d+)-(\d+)(\s)(\d+):(\d+)) 上传'
            if re.search(img_attach, post_content):
                post_content = re.sub(img_attach, '', post_content)
            post_content = re.sub(tail_pattern, '', post_content)
            # csv格式去除帖子内容中的空格
            if 'csv' in self.config["write_mode"]:
                post_content = re.sub(r'\s', '', post_content)

            try:
                score_peoplenum = page.xpath('//*[@id="ratelog_{pstmsgid}"]/dd/table/tr/th[1]/a/span'.format_map(vars()))
                score = page.xpath('//*[@id="ratelog_{pstmsgid}"]/dd/table/tr/th[2]/i/span'.format_map(vars())) 
                content['score'] = score[0].text
                content['score_num'] = score_peoplenum[0].text
            except:
                content['score'] = False
                content['score_num'] = False
        except IndexError:
            # 该帖被管理员或版主屏蔽
            
            postmsg_xpath = '//*[@id="pid{pstmsgid}"]/tr[1]/td[2]/div[2]/div/div'.format_map(vars())
            post_content = page.xpath(postmsg_xpath)[0].text
            content['quote_status'] = 'NA'
            content['tail'] = 'NA'
            content['bilibili_heimu'] = 'NA'
            content['score'] = 'NA'
            content['score_num'] = 'NA'
            if post_content == '提示:':
                post_content = '该帖被管理员或版主屏蔽'
            elif post_content != '此帖仅作者可见':
                raise Exception

        content['post_content'] = post_content
        return content

    def get_author_info(self, page, pstmsgid):
        '''获得该帖的发帖人信息，包括ID、uid、注册时间、精品数、战斗力、历史发帖数、积分、等级'''
        author = {}
        try:
            info = page.xpath('//*[@id="favatar{pstmsgid}"]/div[4]/table'.format_map(vars()))[0]       
            info = self.deal_garbled(info)
            authi_uid = page.xpath('//*[@id="favatar{pstmsgid}"]/div[1]/div/a/@href'.format_map(vars()))[0]
            author['author'] = page.xpath('//*[@id="favatar{pstmsgid}"]/div[1]/div/a'.format_map(vars()))[0].text
            author['author_uid'] = re.findall(r'\d+', authi_uid)[0]
            author['register_time'] = page.xpath('//*[@id="favatar{pstmsgid}"]/dl[2]/dd[2]'.format_map(vars()))[0].text
            author['points'] = page.xpath('//*[@id="favatar{pstmsgid}"]/dl[1]/dd/a'.format_map(vars()))[0].text
            author['level'] = page.xpath('//*[@id="favatar{pstmsgid}"]/p[1]/em/a'.format_map(vars()))[0].text
                
            try:
                author['recommend'] = re.findall(r'(\d+)精华', info)[0]        
                author['zhandouli'] = re.findall(r'华(.*)战斗力', info)[0]
                author['history_postnum'] = re.findall(r'(\d+)帖子', info)[0]
            except IndexError:
                author['history_postnum'] = re.findall('力(.*)帖子', info)[0]
        except IndexError:
            # 作者被删除
            info = page.xpath('//*[@id="favatar{pstmsgid}"]/div'.format_map(vars()))[0].text
            author['author'] = re.findall(r'\r\n(.*)', info)[0]
            author['author_uid'] = 'NA'
            author['register_time'] = 'NA'
            author['points'] = 'NA'
            author['level'] = 'NA'
            author['recommend'] = 'NA'        
            author['zhandouli'] = 'NA'
            author['history_postnum'] = 'NA'

        return author

    def get_floor(self, page, pstmsgid, floor_up):
        '''获取该帖的楼层'''
        try:
            floor_xpath = '//*[@id="postnum{pstmsgid}"]/em'.format_map(vars())
            floor = page.xpath(floor_xpath)[0].text
            return floor
        except IndexError:
            floor_xpath = '//*[@id="postnum{pstmsgid}"]'.format_map(vars())
            floor = page.xpath(floor_xpath)[0].text
            if floor == '\r\n楼主':
                floor = 1
            else:
                floor_up += floor_up
                floor = '来自' + str(floor_up)
            return floor

    def get_edit_status(self, page, pstmsgid):
        '''获取该帖的编辑状况：是否编辑、编辑时间、编辑者'''
        edit_status = {}
        edit_status_xpath = '//*[@id="postmessage_{pstmsgid}"]/*[@class="pstatus"]/text()'.format_map(vars())
        edit_status_motto = page.xpath(edit_status_xpath) # edit status
        if edit_status_motto == []:
            edit_status['edit_status'] = False
            edit_status['edit_time'] = False 
            edit_status['editor'] = False
        else:
            edit_status['edit_status'] = True
            edit_status['edit_time'] = re.findall(r'\d{4}-\d+-\d+\s\d+:\d+', edit_status_motto[0])[0] # edit time
            edit_status['editor'] = re.findall(r'由\s(.*)\s于', edit_status_motto[0])[0] #editor
        return edit_status

    def get_one_post(self, page, pstmsgid):
        '''获取一条帖子的所有情况'''
        post = self.get_post_context(page, pstmsgid)
        edit_status = self.get_edit_status(page, pstmsgid)
        author = self.get_author_info(page, pstmsgid)

        post_time_xpath = '//*[@id="authorposton' + str(pstmsgid) + '"]'
        post_time_motto = page.xpath(post_time_xpath)[0].text
        post['post_time'] = re.findall(r'\d{4}-\d+-\d+\s\d+:\d+', post_time_motto)[0]

        post = OrderedDict({**post, **edit_status, **author})
        return post

    def start(self):
        threadNum = 771602
        pageNum = 1
        sessions = self.loginSession()
        Page = self.get_page(sessions, threadNum, pageNum)
        # author = self.get_author_info(Page, 564011)
        # post = self.get_one_post(Page, 20756)
        # index = self.get_Index(Page)
        # pst = self.get_pstmsgid(Page)
        post = self.get_one_post(Page, 46713862)
        print(post)

# start = time.process_time()
# config_path = os.path.split(
#         os.path.realpath(__file__))[0] + os.sep + 'config.json'
# if not os.path.isfile(config_path):
#     sys.exit(u'当前路径：%s 不存在配置文件config.json' %
#                 (os.path.split(os.path.realpath(__file__))[0] + os.sep))
# with open(config_path, encoding = 'utf-8-sig') as f:
#     config = json.loads(f.read())

# Stage1stParser(config).start()
# end = time.process_time()
# print(end - start)