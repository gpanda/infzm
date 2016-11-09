#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import json
from basic import create_session, timeit
from driver import LOGIN_URL, AUTH2, PREFIX_00, COOKIEJAR_FNAME,\
    INFZMPaperFeeder

__author__ = 'gpanda'

PY_ROOT=os.path.abspath(__file__)
sys.path.append(PY_ROOT)


def load_urls(fname):
    with open(fname) as f:
        urls = json.loads(f.read())
    print(type(urls))
    return urls

@timeit
def fetch_news():
    sess, rc = create_session(LOGIN_URL, AUTH2, COOKIEJAR_FNAME)
    if not 200 <= rc <= 299:
        print("Failed to create session.")
        return
    latest = True
    paper = None
    urls = {'latest': PREFIX_00}
    if len(sys.argv) > 1:
        latest = False
        fname = sys.argv[1]
        print("download with a url list in a file")
        urls = load_urls(fname)
    for date, url in urls.iteritems():
        print("Downloading [{0}]:[{1}]".format(date, url))
        feeder = INFZMPaperFeeder(url=url, sess=sess)
        feeder.crawl()
        paper = feeder.get_paper()
    if latest:
        if os.path.exists("latest"):
            os.remove("latest")
        os.symlink(paper.epub_file_name, "latest")


def main():
    print("For my lovely dad!")
    fetch_news()


if __name__ == '__main__':
    main()