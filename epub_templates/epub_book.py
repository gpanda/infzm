#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import shutil
from collections import OrderedDict
from basic import download_image, replace_regex

__author__ = 'gpanda'


class EPubBook(object):

    env = None

    def __init__(self, raw = None, _type='book'):
        self._type = _type
        self.raw = raw
        self.book = None
        self.epub_root = ''
        self.epub_file_name = ''

    def cook(self, raw):
        self.raw = raw
        # initialize epub meta-data and templates
        self.cook_init()
        # cook book pages
        self.book.cook(self.epub_root)
        # cook content.opf and toc.ncx pages
        self.cook_opf()
        self.cook_toc_ncx()
        self.publish()

    def publish(self):
        self.epub_file_name = self.book.title + "[" + self.book.date + "]"\
                              + ".epub"
        shutil.make_archive(self.epub_file_name, 'zip', self.epub_root)
        shutil.move(self.epub_file_name + ".zip", self.epub_file_name)

    def cook_init(self):
        None

    @classmethod
    def cook_page(cls, template, data, path):
        page_text = template.render(data.__dict__)
        dirname = os.path.dirname(path)
        if dirname != '' and not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(path, 'wb') as f:
            f.write(page_text)
            f.close()

    def cook_opf(self):
        None

    def cook_toc_ncx(self):
        None

    # def unicodify(self):
    #     unicodify(self.__dict__)


class Book(object):

    index_template = None

    def __init__(self):
        self.title = ''
        self.url = ''
        self.date = ''
        self.vol_iss = ''
        self.language = ''
        self.desc_short = ''
        self.compiler = ''
        self.contributor = ''
        self.publisher = ''
        self.subject1 = ''
        self.subject2 = ''
        self.master_head_image = Image()
        self.cover = Image()
        self.back_cover = Image()
        self.index = Index()
        self.chapters = OrderedDict()

    def cook(self, book_root_dir):
        fullpath = book_root_dir + os.sep + self.index.page.path
        EPubBook.cook_page(self.__class__.index_template, self, fullpath)
        for chapter in self.chapters.itervalues():
            chapter.cook(book_root_dir)


class Chapter(object):

    index_template = None

    def __init__(self):
        self.title = ''
        self.order = -1
        self.path = ''
        self.index = Index()
        self.articles = OrderedDict()
        self._prev = None
        self._next = None
        self._parent = None

    def cook(self, book_root_dir):
        fullpath = book_root_dir + os.sep + self.path + os.sep \
                   + self.index.page.path
        EPubBook.cook_page(self.__class__.index_template, self, fullpath)
        for article in self.articles.itervalues():
            article.cook(book_root_dir)


class Article(object):

    article_template = None

    def __init__(self):
        self.url = ''
        self.title = ''
        self.date = ''
        self.created = ''
        self.order = -1
        self.path = ''
        self.id = ''
        self.article = ''
        self.page = None
        self.images = []
        self._prev = None
        self._next = None
        self._parent = None

    def cook(self, book_root_dir):
        full_path_a = book_root_dir + os.sep + self._parent.path \
                      + os.sep + self.path
        full_path_p = full_path_a + os.sep + self.page.path
        for img in self.images:
            full_path_i = full_path_a + os.sep + img.path
            format = download_image(img.url, full_path_i)
            if format != 'jpeg':
                path, ext = os.path.splitext(img.path)
                img.path = path + '.' + format
                img.media_type = "image/" + format
            # replace the image url with local relative path
            self.article = replace_regex(img.url, img.path, self.article)
        EPubBook.cook_page(self.__class__.article_template, self, full_path_p)


class Image(object):
    def __init__(self):
        self.title = ''
        self.name = ''
        self.order = -1
        self.id = ''
        self.path = ''
        self.media_type = ''
        self.url = ''


class Index(object):

    def __init__(self):
        self.items = OrderedDict()
        self._parent = None
        self.id = ''
        self.page = None


class IndexItem(object):

    def __init__(self, label, target):
        self.label = label
        self.target = target
        self._prev = None
        self._next = None


class EPubPage(object):

    def __init__(self):
        self.cooked = ''
        self.order = -1
        self.id = ''
        self.path = ''
        self.url = ''
        self.media_type = ''


if __name__ == '__main__':
    None
