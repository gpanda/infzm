#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from PIL import Image
import StringIO

import datetime
import errno
import json
import os
import pickle
import pytz
import re
import requests
import shutil
import sys
import time
import threading
import uuid

__author__ = 'gpanda'

os.environ['PY_ROOT'] = os.path.abspath(os.path.dirname(__file__))

"""References:

[1] regex, https://docs.python.org/2/library/re.html
[2] https://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""

reload(sys)
sys.setdefaultencoding('utf8')

UTF8_ENCODING = 'UTF-8'

# http request header patterns
HTTP_HEADER_CONTENT_TYPE_CHARSET_REGEX = r'charset=(\w+)'

# HTML <img> url pattern
HTML_IMG_URL_REGEX = r'<img\s+.*src="([^"]+)".*/>'

# CAMOUFLAGE
HDRS = {
    'User-Agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/45.0"',
}

TIMEZONE = 'Asia/Shanghai'
MAX_RETRY = 3


# =============================================================================

def timeit(func):

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
        # return _wrapper(*args, **kwargs)

    def _wrapper(*args, **kwargs):
        ts = time.time()
        rc = func(*args, **kwargs)
        te = time.time()
        td = te - ts
        _args = ''
        if args:
            _args += json.dumps(str(args))
        if kwargs:
            _args += json.dumps(str(kwargs))
        _thread = threading.current_thread()
        print("\n======================== > TIMEIT > =========================")
        print((
                 "Duration: [{time}]\n"
               + "  Thread: [{thread}]\n"
               + "    Func: [{func}]\n"
               + "    Args: [{args}]\n")\
              .format(time=td, thread=_thread.name,
                      func=func.func_name, args=_args
                      )
             )
        print("======================== < TIMEIT < =========================\n")
        sys.stdout.flush()
        return rc

    return wrapper


def save_cookies(cookiejar, fname):
    save_object(cookiejar, fname)


def load_cookies(fname):
    return load_object(fname)


def save_object(obj, fname):
    with open(fname, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_object(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)


# @profile
@timeit
def login(url, auth=None, cookies=None):
    s = requests.Session()
    s.headers.update(HDRS)
    if cookies:
        s.cookies = cookies
        r = s.get("http://www.infzm.com/enews/infzm")
        return s, r.status_code
    r = s.post(url, data=auth)
    return s, r.status_code


# @profile
@timeit
def create_session(url, auth=None, cookie_fname=None):
    # login
    cookiejar = None
    if cookie_fname and os.path.exists(cookie_fname):
        cookiejar = load_cookies(cookie_fname)
    sess, rc = login(url, auth, cookiejar)
    if rc < 200 or rc > 299:
        print("Failed to login. [Status code:%d]" % rc)
    elif not cookiejar and cookie_fname:
        save_cookies(sess.cookies, cookie_fname)
    return sess, rc


# @profile
@timeit
def get_page_content(url, s=None, retry=False):
    """."""
    content = None

    def do_get(url):
        if s:
            return s.get(url)
        else:
            return requests.get(url)

    def resp_failed(r):
        return r.status_code < 200 or r.status_code > 299

    try:
        r = do_get(url)
        if retry and resp_failed(r):
            i = 0
            while i < MAX_RETRY:
                r = do_get(url)
                if not resp_failed(r):
                    break
        if resp_failed(r):
            return None, r.status_code

        encoding = r.encoding
        ct_hdr = r.headers['Content-Type']
        if ct_hdr:
            m = re.search(HTTP_HEADER_CONTENT_TYPE_CHARSET_REGEX, ct_hdr)
            if m:
                encoding = m.group(1)
        content = r.content
        if content:
            content = content.decode(encoding)
            content = content.encode(UTF8_ENCODING)
    except IOError:
        print("Error occurred during request of ({url}) "\
              .format(url=url))

    return content, r.status_code


def search_regex(regex, string):
    results = None
    if string:
        results = re.findall(regex, string, re.U|re.S)
    return results


def replace_regex(regex, repl, string):
    return re.sub(regex, repl, string)


def create_dir(name):
    if not os.path.exists(name):
        try:
            os.makedirs(name)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


def copy(src, dst):
    shutil.copy2(src, dst)


def copytree(src, dst):
    shutil.copytree(src, dst)


def download_image(url, fname):
    dirname = os.path.dirname(fname)
    if dirname != '' and not os.path.exists(dirname):
        os.makedirs(dirname)
    r = requests.get(url)
    i = Image.open(StringIO.StringIO(r.content))
    pathname, ext = os.path.splitext(fname)
    newfname = pathname + '.' + i.format.lower()
    i.save(newfname, i.format)
    return i.format.lower()


def get_uuid():
    return uuid.uuid4()


def get_timestamp():
    tz=pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz=tz)
    return now.isoformat()


def unicodify(adict, encoding='utf-8'):
        for k, v in adict.iteritems():
            if isinstance(k, str):
                k = unicode(k, encoding)
            if isinstance(v, dict):
                unicodify(v, encoding)
            else:
                if isinstance(v, str):
                    v = unicode(v, encoding)


def debug_me():
    import pdb
    pdb.set_trace()
    me = 'gpanda'

# =============================================================================


def test4_f():
    r = requests.get('http://www.infzm.com/enews/infzm/5217')
    print(r.text)


def test4():
    # Fill in your details here to be posted to the login form.
    payload = {
        'loginname': 'retaelppa@gmail.com',
        'password': 'rlt2880009'
    }

    # Use 'with' to ensure the session context is closed after use.
    with requests.Session() as s:
        LOGIN_URL = 'http://passport.infzm.com/passport/login'
        p = s.post(LOGIN_URL, data=payload)
        # print the html returned or something more intelligent to see if it's a successful login page.
        print(p.text)

        # An authorised request.
        r = s.get('http://www.infzm.com/enews/infzm/5217')
        print(r.text)
        # etc...


if __name__ == '__main__':
    #test4()
    #test4_f()
    None
