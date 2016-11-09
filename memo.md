Parse strategy
==============

* crawl current issue
* crawl all earlier issues (most of the time this is needed only once)


Site map
========
Portal and latest issue contents page:
http://www.infzm.com/enews/infzm

Some earlier issue contents page:
http://www.infzm.com/enews/infzm/5217

Some article pages:
http://www.infzm.com/content/120343
http://www.infzm.com/content/120388
http://www.infzm.com/content/120205

Article categories:
新闻
http://www.infzm.com/contents/5
新闻2页
http://www.infzm.com/contents/5/1
时政3页
http://www.infzm.com/contents/11/2

```json
{ 5: u'新闻', 6: u'经济', 7: u'文化', 8: u'评论',
  9: u'图片', 10: u'生活', 11: u'时政', 12: u'社会',
  13: u'科技', 3981: u'电影报道', 1374: u'绿色'}
```

A special category
'http://www.infzm.com/voice': u'囧囧有声'

Page structure
==============

Current issue page
------------------
```html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>南方周末</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
...
</head>
<body>
...
<header class="clearfix">
...
 <nav class="clearfix">
    <ul>
     <li class=""><a target="_blank" href="http://www.infzm.com/news.shtml">新闻</a></li>
	 <li class=""><a target="_blank" href="http://www.infzm.com/economy.shtml">经济</a></li>
	 <li class=""><a target="_blank" href="http://www.infzm.com/culture.shtml">文化</a></li>
	 <li class=""><a target="_blank" href="http://www.infzm.com/review.shtml">评论</a></li>
	 <li class="life"><a href="http://www.infzm.com/life.shtml">生活</a></li>
	 <li class=""><a target="_blank" href="http://www.infzm.com/movie.shtml">电影</a></li>
	 <li class=""><a target="_blank" href="http://www.infzm.com/green.shtml">绿色</a></li>
	 <!--<li class=""><a target="_blank" href="http://www.infzm.com/voice">囧囧有声</a></li>-->
	 <li class=""><a target="_blank" href="http://www.infzm.com/vote.shtml">民调中心</a></li>
    </ul>
  </nav>
</header>
...
<!--CONTENT BEGIN-->
<!--主体-->
<div class="inner col-2lb bgline clearfix" id="enews_index">
<div class="side-1">
<div class="cover">
<img src="http://images.infzm.com/medias/2016/1020/107891.jpeg"/>
<p>2016年10月20日</p>
<p>第1704期</p>
...
<option>选择日期</option>
<option value="http://www.infzm.com/enews/infzm/5208">2016-10-13</option>
<option value="http://www.infzm.com/enews/infzm/5199">2016-10-06</option>
...
</div>
...
<div class="side-2">
<dl class="topnews">
<span>本期头条:</span>
<dt><a href="http://www.infzm.com/content/120421" title="虎口之旅 八达岭野生动物园老虎袭人事件调查">虎口之旅 八达岭野生动物园老虎袭人事件调查</a>
</dt>
<dd class="summary">八达岭野生动物园负责人称，园方对此事不负任何责任，承担15%是基于道义的补偿；拒绝让当事员工受访，“自说自话没有法律效力，以第三方机关的调查为准”。</dd>
</dl>
...
<h2>新闻</h2>
...
<li><a href="http://www.infzm.com/content/120405" title="借力社区营造，中国慈善超市谋变 ">借力社区营造，中国慈善超市谋变 </a></li>
<li><a href="http://www.infzm.com/content/120406" title="“入宫”30天，航天员怎么过？">“入宫”30天，航天员怎么过？</a></li>
...
<h2>xxx</h2>
...
</div>
</div>
<!--CONTENT END-->
</body>
</html>
```

Article page
------------

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>南方周末 - 虎口之旅 八达岭野生动物园老虎袭人事件调查</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
...
</head>
<body>
...
<article>
...
</article>
</body>
</html>
```
