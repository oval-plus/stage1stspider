# -*- coding: utf-8 -*-

import requests
import re
from lxml import etree
import time, sys

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
}
# name = input('please enter ur username')
# pswd = input('please enter ur password')
data = {
    'username':'椭圆',
    'password':'freeaxis666@',
}
url = r'https://bbs.saraba1st.com/2b/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
sessions = requests.Session()
sessions.post(url, data = data, headers = headers)

def thread(id): # tag, thread title, page, section name
    address = 'https://bbs.saraba1st.com/2b/thread-{id}-1-1.html'.format_map(vars())
    h = sessions.get(address, headers = headers)
    
    # getting tag
    h_text = h.text
    pattern = '(.*)typeid(.*?).*\[(?P<tag_name>.*)\]' #tag regular expression
    search_result = re.search(pattern,h_text)
    if search_result:
        target_text = search_result.groupdict()['tag_name']
    else:
        target_text = "no tag"

    # path=r'C:\Users\Oval Liu\Desktop\douban.txt'
    # with open(path,"w",encoding='utf-8') as f:
    #     f.write(h_text)
    # with open(path,"r",encoding='utf-8') as f:
    #     pattern='(.*)typeid(.*?).*' #tag regular expression
    #     test=f.readline()
    #     while test:
    #         if re.search(pattern,test):
    #             test_ = re.match(pattern,test).group()
    #             # print(test_)
    #             k_l=test_.find('[')
    #             k_r=test_.find(']')
    #             tag=test_[k_l+1:k_r] #tag
    #             print(tag)
    #             test = f.readline()
    #             break
    #         else:
    #             test = f.readline()
    #             pass
    #         continue
    # with open(path,'w',encoding='utf-8') as f:
    #     f.truncate()

    root = etree.HTML(h_text)
    fenqu = root.xpath('//*[@id="pt"]/div/a[4]')[0].text #Section name
    subject = root.xpath("//span[@id = 'thread_subject']")[0].text #thread title
    alert = root.xpath('//*[@id="messagetext"]/text()')
    if alert != []:
        subject = '抱歉，Obey or Die'

    # page
    page_motto = root.xpath('//*[@id="pgt"]/div/div/label/span')[0].text
    page = re.findall(r'\d+', page_motto)[0]
    # print(page)

    return page, target_text, subject, fenqu, id

# print(thread(1500001))

def deal_garbled(info):
    """处理乱码"""
    info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
        sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
    # info = (info.xpath('string(.)').replace(u'\u200b', ''))
    return info

def tiezi(id, p): # 每一页上的帖子，发帖人，编辑情况（包括编辑者与编辑时间）
    test_add = 'https://bbs.saraba1st.com/2b/thread-{id}-{p}-1.html'.format_map(vars())
    h = sessions.get(test_add, headers=headers)

    # font_rule = re.compile(r'<font+(.*?)>|</font>|<strong>|</strong>') # 处理帖子css
    # h = re.sub(font_rule, '', h.text)
    root = etree.HTML(h.text)

    selected_postid = []
    context = root.xpath('//*[@id="postlist"]//div/@id')
    postid_rule = re.compile(r'post_[0-9]+')
    for i in range(0,len(context)): #get post id
        if re.search(postid_rule, context[i]):
            selected_postid.append(context[i])
        else:
            i += i
    for j in range(0,len(selected_postid)):
        pstmsgid = selected_postid[j][5:]
        j += j
        author_xpath = '//*[@id="favatar{pstmsgid}"]/div[1]/div/a'
        author_xpath = author_xpath.format_map(vars())
        author_name = root.xpath(author_xpath)[0].text #发帖人

        # 帖子发表时间
        post_time_motto = root.xpath('//*[@id="authorposton{pstmsgid}"]/text()'.format_map(vars()))[0]
        post_time = re.findall(r'\d{4}-\d+-\d+\s\d+:\d+', post_time_motto)[0]

        # 帖子编辑时间与编辑者
        edit_status_xpath = '//*[@id="postmessage_{pstmsgid}"]/*[@class="pstatus"]/text()'.format_map(vars())
        edit_status_motto = root.xpath(edit_status_xpath) # edit status
        if edit_status_motto == []:
            edit_status = 'F'
            edit_time = 'F' 
            editor = 'NA'
        else:
            edit_status = 'T'
            edit_time = re.findall(r'\d{4}-\d+-\d+\s\d+:\d+', edit_status_motto[0])[0] # edit time
            editor = re.findall(r'由\s(.*)\s于', edit_status_motto[0])[0] #editor

        # 帖子本体
        postmsg_xpath = '//*[@id="postmessage_{pstmsgid}"]'
        postmsg_xpath = postmsg_xpath.format_map(vars())
        postmsg = root.xpath(postmsg_xpath)[0]
        postmsg = deal_garbled(postmsg)

        # poster = root.xpath('//*[@id="postmessage_46281560"]/div[1]/blockquote/font/a/font')[0]
        # print(poster[0].text)
        quote = root.xpath('//*[@id="postmessage_46281560"]/div[1]/blockquote')[0]

        # poster = deal_garbled(poster)
        quote = deal_garbled(quote)

        # print(author_name, post_time, postmsg, poster, quote)
        print(quote)

tiezi(1911165, 1)
# tiezi(1729918, 1)
def WriteTest(start, end):
    path=r'C:\Users\Oval Liu\Desktop\douban.txt'
    with open(path,"w",encoding='utf-8') as f:
        floorLine = "\n" + u"-----------------------------------------------------------------------------------------\n"
        for id in (start, end):
            f.write(str(thread(id)))
            f.write(floorLine)
            page = thread(id)[0]
            for p in (1, page):
                f.write(str(tiezi(id, p)))
                f.write(floorLine)

# WriteTest(1500002, 1500004)