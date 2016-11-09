#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from jinja2 import Environment, PackageLoader
import unittest
import sys
sys.path.append("..")
from basic import (create_session, save_object, load_object)
from driver import (LOGIN_URL, AUTH2, PREFIX_00, COOKIEJAR_FNAME,
                    INFZMPaperFeeder)
from epub_templates.infzm_t import INFZMPaper

__author__ = 'gpanda'


class TestINFZMPaper(unittest.TestCase):

    def setUp(self):
        None


    def tearDown(self):
        None


    def test_builder(self):
        env = Environment(loader=PackageLoader('epub_templates', '../epub_templates'))
        t = env.get_template("content.opf")
        feeder = load_object("feeder.dat")
        paper = feeder.get_paper()
        # paper.unicodify()
        text = t.render(paper.book.__dict__)
        print(text)
        self.assertTrue(("gpanda" in text))


    def test_0_crawling_paper(self):
        None
        # self.crawl_paper()

    # Avoid real web requests everytime, run once and persist
    # the webcontent object
    def crawl_paper(self):
        sess, rc = create_session(LOGIN_URL, AUTH2, COOKIEJAR_FNAME)
        self.assertTrue((rc >= 200 and rc < 299))
        # current release
        url = PREFIX_00
        feeder= INFZMPaperFeeder(url=url, sess=sess)
        feeder.crawl()
        #feeder.print_all_in_one()
        save_object(feeder, "feeder.dat")


    def test_1_coverter(self):
        feeder = load_object("feeder.dat")
        #print(feeder.url)
        self.assertTrue(feeder.url == PREFIX_00)
        paper = feeder.get_paper()
        print(paper.book.url)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestINFZMPaper)
    unittest.TextTestRunner(verbosity=2).run(suite)

