#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
from jinja2 import Environment, PackageLoader
from basic import \
        (get_uuid, get_timestamp, create_dir, copy, copytree, download_image)
from epub_book import \
    (EPubBook, Book, Chapter, Article, Image, IndexItem, EPubPage)


__author__ = 'gpanda'

sys.path.append("..")


class EPubINFZMPaper(EPubBook):

    env = Environment(loader=PackageLoader('epub_templates', '.'))
    content_opf_template = env.get_template("content.opf")
    toc_ncx_template = env.get_template("toc.ncx")

    def __init__(self):
        super(EPubINFZMPaper, self).__init__()
        self._type = 'news.w'
        self.epub_root = ''
        self.book = INFZMPaper()

    def cook_init(self):
        # init paper meta info
        self.book.url = self.raw['url']
        self.book.date = self.raw['date']
        self.book.vol_iss = self.raw['vol_iss']
        self.book.cover.url = self.raw['cov_img_url']
        self.book.cover.media_type = "image/jpeg"
        # init epub book root directory
        self.epub_root = self.book.date + os.sep + "epub"

        # construct book content out of raw data structure
        # book index page
        page = INFZMPage()
        page.path = "index.html"
        self.book.index.page = page
        pi = 1  # page order in a book
        ci = 0  # chapter order in a book
        _prev_c = None
        for c, v in self.raw['contents'].iteritems():
            if 'articles' in v:
                # chapter
                chapter = INFZMPaperCategory()
                if _prev_c:
                    _prev_c._next = chapter
                chapter._prev = _prev_c
                _prev_c = chapter
                chapter._parent = self.book
                chapter.title = c
                chapter.order = str(ci)
                chapter.path = "c" + chapter.order
                # chapter index page
                page = INFZMPage()
                page.title = chapter.title
                page.order = str(pi)
                page.id = "id" + page.order
                page.path = "index_{i}.html".format(i=page.order)
                chapter.index.page = page
                # add an book index item for this chapter
                item = IndexItem(chapter.title, chapter.index.page)
                self.book.index.items[item.label] = item
                # add this chapter in the book
                self.book.chapters[chapter.title] = chapter
                pi += 1
                ai = 0  # article order in a chapter
                _prev_a = None
                for u, a in v['articles'].iteritems():
                    # article
                    article = INFZMPaperArticle()
                    article.timestamp = get_timestamp()
                    if _prev_a:
                        _prev_a._next = article
                    article._prev = _prev_a
                    _prev_a = article
                    article._parent = chapter
                    article.url = u
                    article.title = a['title']
                    article.order = str(ai)
                    article.path = "a" + article.order
                    article.article = a['article']
                    # article page
                    page = INFZMPage()
                    page.title = article.title
                    page.order = str(pi)
                    page.id = "id" + page.order
                    page.path = "index_{i}.html".format(i=page.order)
                    article.page = page
                    # add an chapter index item for this article
                    item = IndexItem(article.title, article.page)
                    chapter.index.items[item.label] = item
                    # add this article in the chapter
                    chapter.articles[article.title] = article
                    k = 0  # image order in an article
                    for url in a['images']:
                        # image
                        img = Image()
                        img.order = str(k)
                        img.url = url
                        img.path = "images{sep}img{k}_{i}.jpeg"\
                            .format(k=img.order, i=page.order, sep=os.sep)
                        img.id = 'img{k}_{i}'\
                            .format(k=img.order, i=page.order)
                        img.media_type = 'image/jpeg'

                        k += 1
                        # add image in the article
                        article.images.append(img)
                    ai += 1
                    pi += 1
                ci += 1

        self.setup_epub_root()

    def setup_epub_root(self):
        create_dir(self.epub_root)
        template_root = os.environ['PY_ROOT'] + os.sep + "epub_templates"
        copy(template_root + os.sep + "headerLogo.png", self.epub_root)
        self.book.master_head_image.path = self.book.master_head_image.name
        copy(template_root + os.sep + "mimetype", self.epub_root)
        copy(template_root + os.sep + "page_styles.css", self.epub_root)
        copy(template_root + os.sep + "stylesheet.css", self.epub_root)
        copy(template_root + os.sep + "titlepage.xhtml", self.epub_root)
        meta_inf = self.epub_root + os.sep + "META-INF"
        if not os.path.exists(meta_inf):
            copytree(template_root + os.sep + "META-INF", meta_inf)
        dl_path = self.epub_root + os.sep + self.book.cover.name
        self.book.cover.path = self.book.cover.name
        download_image(self.book.cover.url, dl_path)

    def cook_opf(self):
        path = self.epub_root + os.sep + "content.opf"
        self.cook_page(self.__class__.content_opf_template, self.book, path)

    def cook_toc_ncx(self):
        path = self.epub_root + os.sep + "toc.ncx"
        self.cook_page(self.__class__.toc_ncx_template, self.book, path)


class INFZMPaper(Book):

    index_template = EPubINFZMPaper.env.get_template("index.html")

    def __init__(self):
        super(INFZMPaper, self).__init__()
        # constants
        self.title = '南方周末'
        self.language = 'zh-Hans'
        self.desc_short = '在这里，读懂中国'
        self.author = 'Gpanda Ren'
        self.compiler = 'Gpanda Ren'
        self.contributor = 'Gpanda Ren'
        self.publisher = 'Gpanda Ren'
        self.subject1 = '新闻'
        self.subject2 = '南方周末'
        self.master_head_image.name = 'headerLogo.png'
        self.cover.name = 'cover.jpeg'
        self.timestamp = get_timestamp()
        self.uuid = get_uuid()


class INFZMPaperCategory(Chapter):

    index_template = EPubINFZMPaper.env.get_template("chapter_index.html")

    def __init__(self):
        super(INFZMPaperCategory, self).__init__()


class INFZMPaperArticle(Article):

    article_template = EPubINFZMPaper.env.get_template("article.html")

    def __init__(self):
        super(INFZMPaperArticle, self).__init__()


class INFZMPage(EPubPage):

    def __init__(self):
        self.media_type = "application/xhtml+xml"


if __name__ == '__main__':
    None
