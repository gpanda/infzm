#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import Queue
import os
import sys
import json
from collections import OrderedDict
from basic import create_session, timeit, do_together
from driver import LOGIN_URL, AUTH2, PREFIX_00, COOKIEJAR_FNAME,\
    INFZMPaperFeeder

__author__ = 'gpanda'


PY_ROOT = os.path.abspath(__file__)
sys.path.append(PY_ROOT)


def load_urls(fname):
    with open(fname) as f:
        data = json.loads(f.read())
    urls = OrderedDict()
    for date, url in data.iteritems():
        urls[date] = url
    return urls


def concurrent_fetch_news(sess, queue):
    try:
        while not queue.empty():
            (date, url) = queue.get(False)
            do_fetch_news(sess, date, url)
            queue.task_done()
    except Queue.Empty as e:
        # print(e)
        None
    return


@timeit
def do_fetch_news(sess, date, url):
    print("\nDownloading [{0}]:[{1}]".format(date, url))
    sys.stdout.flush()
    feeder = INFZMPaperFeeder(url=url, sess=sess)
    feeder.crawl()
    return feeder.get_paper()


@timeit
def fetch_news():
    sess, rc = create_session(LOGIN_URL, AUTH2, COOKIEJAR_FNAME)
    if not 200 <= rc <= 299:
        print("Failed to create session.")
        return
    latest = True
    paper = None
    urls = OrderedDict()
    urls['latest'] = PREFIX_00
    if len(sys.argv) > 1:
        latest = False
        fname = sys.argv[1]
        print("download with a url list in a file")
        urls = OrderedDict(reversed(sorted(load_urls(fname).items())))
    if latest:
        paper = do_fetch_news(sess, urls.keys()[0], urls.values()[0])
        if not paper:
            return
        if os.path.exists("latest"):
            os.remove("latest")
        os.symlink(paper.epub_file_name, "latest")
        return
    q = Queue.Queue(len(urls.items()))
    worker_num = 8
    for date, url in urls.iteritems():
        q.put((date, url))
    do_together(concurrent_fetch_news, worker_num, sess, q)
    q.join()


def main():
    print("For my lovely dad!\n")
    fetch_news()


if __name__ == '__main__':
    main()
