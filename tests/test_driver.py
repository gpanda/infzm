#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function

import pprint
import sys
sys.path.append("..")
import unittest
from basic import (get_page_content, create_session)
from driver import (LOGIN_URL, AUTH2, INFZMPaperFeeder)

__author__ = 'gpanda'



class TestDriver(unittest.TestCase):

    def test_digest2(self):
        sess, rc = create_session(LOGIN_URL, AUTH2)
        self.assertTrue((200 <= rc <= 299))
        raw, rc = get_page_content("http://www.infzm.com/content/120699", sess)
        self.assertTrue((200 <= rc <= 299))
        (cooked, images) = INFZMPaperFeeder.digest2(raw)
        pprint.pprint(cooked)
        pprint.pprint(images)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDriver)
    unittest.TextTestRunner(verbosity=2).run(suite)
