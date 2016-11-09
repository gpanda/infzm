#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import re
import threading

from basic import (timeit, get_page_content, download_image,
                   load_object, unicodify, create_dir,
                   HTML_IMG_URL_REGEX)
from epub_templates.infzm_t import EPubINFZMPaper

from Queue import Queue
from bs4 import BeautifulSoup
from collections import OrderedDict
from copy import deepcopy

__author__ = 'gpanda'

"""References:

[1] BeautifulSoup, https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    #css-selectors
[2] Easy thread-safe queque, http://pymotw.com/2/Queue/
[3] Jinja2, http://jinja.pocoo.org/docs/dev/templates/
"""

"""Web page patterns:

P1 Contents page
Sample URL: http://www.infzm.com/enews/infzm

 D1 cover

  D1.1 image
  D1.2 release date
  D1.3 release No.

  S1
  <div class="cover">
    <img src="http://images.infzm.com/medias/2016/1020/107891.jpeg"/>
    <p>2016年10月20日</p>
    <p>第1704期</p>

 D2 topnews

  D2.1 '本期头条'
  D2.2 URL
  D2.3 title
  D2.4 summary

  S2
  <dl class="topnews">
    <span>本期头条:</span>
    <dt><a href="http://www.infzm.com/content/120421" title="虎口之旅 八达岭野生动物园老虎袭人事件调查">虎口之旅 八达岭野生动物园老虎袭人事件调查</a>
    </dt>
    <dd class="summary">八达岭野生动物园负责人称，园方对此事不负任何责任，承担15%是基于道义的补偿；拒绝让当事员工受访，“自说自话没有法律效力，以第三方机关的调查为准”。</dd>
  </dl>

 D3 contents

  D3.1 category
   D3.1.1 link1
   D3.1.2 link2
   ...
   D3.1.n linkn

   S3
   <h2>新闻</h2>
   <dl>
     <dt></dt>
     <dd>
       <ul class="relnews">
        <li><a href="http://www.infzm.com/content/120405" title="借力社区营造，中国慈善超市谋变 ">借力社区营造，中国慈善超市谋变 </a></li>
        <li><a href="http://www.infzm.com/content/120406" title="“入宫”30天，航天员怎么过？">“入宫”30天，航天员怎么过？</a></li>
        <li><a href="http://www.infzm.com/content/120407" title="“如果让我选择，我想成为直男” 同性恋“低龄化”现象观察 ">“如果让我选择，我想成为直男” 同性恋“低龄化”现象观察 </a></li>
        <li><a href="http://www.infzm.com/content/120404" title="中国公益慈善思想峰会六年考慈善与社工：分流还是携手？ ">中国公益慈善思想峰会六年考慈善与社工：分流还是携手？ </a></li>
        <li><a href="http://www.infzm.com/content/120414" title="五名刑警的打黑之劫">五名刑警的打黑之劫</a></li>
        <li><a href="http://www.infzm.com/content/120420" title="舆论之“虎” 老虎袭人事件部分流言溯源">舆论之“虎” 老虎袭人事件部分流言溯源</a></li>
       </ul>
     </dd>
   </dl>


NB.
  P1 = Page 1, D1 = Data 1, S1 = Sample 1

P2 Article page
Sample URL: http://www.infzm.com/content/120205

S4
<div id="mainContent">
  ...
  <div id="content">
    ...
    <article>...</article>

"""


# HTML TAGS
HTML_HEADER = r'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
HTML_BEGIN = r'<html xmlns="http://www.w3.org/1999/xhtml">'
HTML_BODY_BEGIN = r'<body>'
HTML_BODY_END = r'</body>'
HTML_END = r'</html>'

HTML_FRONT = u'' + HTML_HEADER + u'\n' + HTML_BEGIN + u'\n' + HTML_BODY_BEGIN
HTML_BACK = u'' + HTML_BODY_END + u'\n' + HTML_END


# Web site specific data
# - Host
SCHEME = 'http://'
HOST = 'www.infzm.com'
# - Issue contents page
PATH_0 = '/enews/infzm/'
PREFIX_00 = SCHEME + HOST + PATH_0
# - Article page
PATH_1 = '/content/'
PREFIX_01 = SCHEME + HOST + PATH_1
# - Auth
LOGIN_URL = 'http://passport.infzm.com/passport/login'
AUTH2 = {
    'loginname': 'retaelppa@gmail.com',
    'password': 'rlt2880009'
}
AUTH = ('retaelppa@gmail.com', 'rlt2880009')
COOKIEJAR_FNAME = 'cookies'

# BOOK
COVER_PAGE = 'cover.htm'
COVER_IMAGE_NAME = 'cover.jpeg'
TOP_NEWS_SUMMARY_PAGE = 'topnews_s.htm'
CONTENTS_PAGE = 'contents.htm'
TOP_NEWS_PAGE = 'topnews.htm'

_CONTENTS = \
{
    '本期头条': {'id': 0},
        '新闻': {'id': 5},     '经济': {'id': 6},   '文化': {'id': 7},
        '评论': {'id': 8},     '图片': {'id': 9},   '生活': {'id': 10},
        '时政': {'id': 11},    '社会': {'id': 12},  '科技': {'id': 13},
        '绿色': {'id': 1374},
        '观点': {'id': 2556},
    '电影报道': {'id': 3981},
}

unicodify(_CONTENTS)

CONTENTS = OrderedDict(
    sorted(_CONTENTS.items(), key = lambda t: t[1]['id'])
)

_PAPER = \
{
    "url": "",
    "date": "",
    "vol_iss": "",
    "cov_img_url": "",
    "contents": None,
}


class INFZMPaperFeeder:

    def __init__(self, url=None, sess=None, date=None, vol_iss=None,
                 cov_img=None, top_news=None, contents=None):
        self.url = url
        self.sess = sess
        self.date = date
        self.vol_iss = vol_iss
        self.cov_img = cov_img
        self.top_news = top_news
        self.contents = contents
        self.raw_paper = deepcopy(_PAPER)

    #@profile
    @staticmethod
    # @timeit
    def digest1(raw):

        rc_1 = (None, None, None, None, None)

        # root = BeautifulSoup(raw, 'html.parser')
        root = BeautifulSoup(raw, 'lxml')

        # cover
        cover = root.select('div[class="cover"]')
        if cover:
            cover = cover[0]
            cov_img = cover.select("img")
            if cov_img:
                cov_img = str(cov_img[0])
            pp = cover.select("p")
            if pp:
                date = str(pp[0].string.strip())
                vol_iss = str(pp[1].string.strip())

        # contents and initialize articles
        contents = deepcopy(CONTENTS)

        # top news
        top_news = root.select("dl[class='topnews']")
        if top_news:
            top_news = top_news[0]

            c = top_news.select("span")[0].string[:-1]
            link = top_news.select("dt a")[0]
            title = str(link["title"])
            url = str(link["href"])
            od = OrderedDict()
            od[url] = {'title': title, 'article': None, 'images': []}
            contents[str(c)]["articles"] = od
            top_news = str(top_news)

        categories = root.select("h2")
        for c in categories:
            od = OrderedDict()
            titles = c.find_next_sibling("dl").select("ul[class='relnews'] a")
            for t in titles:
                title = str(t.string)
                url = str(t['href'])
                od[url] = {'title': title, 'article': None, 'images': []}
            if str(c.string) not in contents:
                contents[str(c.string)] = {'id': -1}

            if len(od.keys()) > 0:
                contents[str(c.string)]["articles"] = od

        return (cov_img, date, vol_iss, top_news, contents)

    @staticmethod
    def digest2(raw):
        root = BeautifulSoup(raw, 'lxml')
        cooked = root.find("article")
        images_bs = cooked.find_all("img")
        images = []
        for image in images_bs:
            results = re.findall(HTML_IMG_URL_REGEX, str(image))
            if results:
                images.append(results[0])

        return str(cooked), images

    # @profile
    # @timeit
    def crawl_articles(self):
        """Central controller of articles crawling.

        ** Preparing working queue (FIFO) and workers for article links.
        ** Retrieving articles, refining and sorting them.

        contents = { # OrderedDict
            "<category0>": {
                "id": 1,
                "articles": { # OrderedDict
                    "<url0>": {
                        "title": "<title>",
                        "article": "<article>",
                        "images": [<img0>, <img1>, ...]
                    },
                    ...
                }
            },
            ...
        }

        """
        # @profile
        # @timeit
        def work(__in, __out):
            for k, v in __in.iteritems():
                while not v.empty():
                    url = v.get()
                    # print(threading.current_thread().name + url)
                    raw, rc = get_page_content(url, self.sess)
                    if 200 <= rc <= 299:
                        article, images = INFZMPaperFeeder.digest2(raw)
                        __out[k].put([url, article, images])
                    else:
                        print("Failed to get web page {0}.[Status code:{1}]"\
                              .format(url, rc))
                        continue

        _in = {}
        _out = {}
        for k, v in self.contents.iteritems():
            if 'articles' in v:
                od = v['articles']
                _in[k] = Queue(len(od))
                _out[k] = Queue(len(od))
                for url in od.iterkeys():
                    _in[k].put(url)

        workers = {}
        # worker_number = config['workers']
        worker_number = 8
        for i in range(worker_number):
            workers[i] = threading.Thread(
                target=work,
                name=str(i),
                args=[_in, _out],
            )
            workers[i].start()

        for worker in workers.values():
            worker.join()

        # LOG.debug("All jobs have been done.")

        for k, v in _out.iteritems():
            while not v.empty():
                url, article, images = v.get()
                od = self.contents[k]["articles"]
                # print(od[url])
                od[url]['article'] = article
                od[url]['images'] = images

    # @profile
    # @timeit
    def crawl_mainpage(self):
        raw, rc = get_page_content(self.url, self.sess)
        if rc >= 200 and rc < 300:
            (self.cov_img, self.date, self.vol_iss, self.top_news,
             self.contents)\
                = INFZMPaperFeeder.digest1(raw)
            return 0
        else:
            print("Failed to get web page. [Status code:%d]" % rc)
            return 1

    # @profile
    # @timeit
    def crawl(self):
        rc = self.crawl_mainpage()
        if rc == 0:
            self.crawl_articles()
        self.update_raw_paper()

    def print_all_in_one(self):

        print(HTML_FRONT)
        # cover image
        print(self.cov_img)
        print("</br>")
        # paper name, url, vol_iss, date
        print(u"<a href=\"{0}\">南都周末电子报 - {1}</a></br>"\
                .format(self.url, self.vol_iss))
        print(u"出版日期: {0}</br>".format(self.date))
        # top news
        print(self.top_news + u"</br>")
        # contents
        for k, v in self.contents.iteritems():
            if 'articles' in v:
                print("<h3>{0}</h3>".format(k))
                for url, article in v['articles'].iteritems():
                    print("<h4>{0}</h4>".format(article['title']))
        # articles
        for k, v in self.contents.iteritems():
            if 'articles' in v:
                print("<h3>{0}</h3>".format(k))
                for url, article in v['articles'].iteritems():
                    print("<h4>{0}</h4>".format(article['title']))
                    print(article['article'])
        print(HTML_BACK)

    def write_page(self, words, name):
        with open(name, 'w') as f:
            f.write(HTML_FRONT)
            f.write(words)
            f.write(HTML_BACK)
            f.close()

    def write_cover(self):
        cov_img_url = re.findall(HTML_IMG_URL_REGEX, self.cov_img)[0]
        download_image(cov_img_url, COVER_IMAGE_NAME)
        words = self.cov_img + u"</br>" + u"\n" \
                + u"<a href=\"{0}\">南都周末电子报 - {1}</a></br>\n"\
                 .format(self.url, self.vol_iss) + u"\n" \
                + u"出版日期: {0}</br>".format(self.date) + u"\n"
        self.write_page(words, COVER_PAGE)

    def write_topnews_s(self):
        words = u""
        words += self.top_news + u"</br>" + u"\n"
        self.write_page(words, TOP_NEWS_SUMMARY_PAGE)

    def write_contents(self):
        words = u""
        for k, v in self.contents.iteritems():
            if 'articles' in v:
                words += "<h3>{0}</h3>".format(k) + u'\n'
                for url, article in v['articles'].iteritems():
                    words += "<h4>{0}</h4>".format(article['title']) + u'\n'
        self.write_page(words, CONTENTS_PAGE)

    def write_topnews(self):
        words = u""
        if 'articles' in self.contents.values()[0]:
            words += self.contents.values()[0]['articles']\
                         .values()[0]['article'] + u"\n"
            self.write_page(words, TOP_NEWS_PAGE)

    def write_articles(self):
        for k, v in self.contents.iteritems():
            if 'articles' in v:
                create_dir(k)
                cwd = os.getcwdu()
                os.chdir(k)
                for url, article in v['articles'].iteritems():
                    words = article['article'] + u'\n'
                    self.write_page(words, article['title'] + ".htm")
                os.chdir(cwd)

    def write(self):
        create_dir(self.date)
        cwd = os.getcwdu()
        os.chdir(self.date)

        self.write_cover()
        self.write_topnews_s()
        self.write_contents()
        self.write_topnews()
        self.write_articles()

        os.chdir(cwd)

    def update_raw_paper(self):
        self.raw_paper['url'] = self.url
        self.raw_paper['date'] = self.date
        self.raw_paper['vol_iss'] = self.vol_iss
        self.raw_paper['cov_img_url'] = \
            re.findall(HTML_IMG_URL_REGEX, self.cov_img)[0]
        self.raw_paper['contents'] = self.contents

    def get_paper(self):
        paper = EPubINFZMPaper()
        paper.cook(self.raw_paper)
        return paper


def test():
    # sess, rc = create_session(LOGIN_URL, AUTH2, COOKIEJAR_FNAME)
    # if rc < 200 or rc > 299:
    #     print("Error occurred during session creation.")
    # # current release
    # url = PREFIX_00
    # feeder= INFZMPaperFeeder(url=url, sess=sess)
    # feeder.crawl()
    # feeder.print_all_in_one()
    # feeder.write()
    # save_object(feeder, "feeder.dat")
    feeder2 = load_object("feeder.dat")
    print(feeder2.url)
    # paper = feeder2.get_paper()

if __name__ == '__main__':
    test()
