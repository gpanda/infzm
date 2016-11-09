#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function

import os
import sys
sys.path.append("..")
import unittest

from basic import (download_image, create_session, get_timestamp, search_regex,
                   replace_regex, HTML_IMG_URL_REGEX)

__author__ = 'gpanda'



class TestBasic(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_create_session(self):
        login_url = 'http://passport.infzm.com/passport/login'
        auth2 = {
            'loginname': 'retaelppa@gmail.com',
            'password': 'rlt2880009'
        }
        COOKIEJAR_FNAME = 'cookies'
        sess, rc = create_session(login_url, auth2)
        self.assertTrue((200 <= rc <= 299))

    def test_download_image(self):
        url = "https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2@2x.png"
        fname = "wikilogo.png"
        format = download_image(url, fname)
        self.assertTrue(format == 'png')
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)

    def test_image_url_regex(self):
        src = r'<img alt="" class="landscape" height="440" src="http://images.infzm.com/medias/2016/1020/107885.jpeg@660x440" style="text-align: center;" width="660"/>'
        print("search img tag for img url:[" + src + "]")
        url = ''
        results = search_regex(HTML_IMG_URL_REGEX, src)
        if results:
            url = results[0]
        print("url:[" + url + "]")
        newsrc = replace_regex(url, "images/img0_2.jpeg", src)
        print("after replace, \nsrc:[" + src + "]\nnewsrc:[" + newsrc + "]")

    def test_get_timestamp(self):
        print(get_timestamp())


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)

