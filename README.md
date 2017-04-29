# scrapbooktools
~ tools for ScrapBook FF ext. usage for myselfe

## background

[ZoomQuiet.io collection mapping {by gen4dot2htm.py v11.10.27 at:160217 11:09:36,660754}](http://zoomquiet.io/collection.html)

使用 scrapbook 本地长期收集积累各种技术资料网页,
原先通过内置发布功能,输出索引页面,然后自动发布到 7牛空间

## problem

问题是网页越来越多, 仅仅是索引页面也快速超过3M 以致加载超时

## fixed

于是简单的, 用 python 解析 ScrapBook 的 RDF 文件,
自动生成对二级目录的分散索引页面, 再发布.

参考: 

- [ScrapBook辅助工具之expidxlevels](http://blog-zq-org.qiniucdn.com/pyblosxom/utility/py4xml/scrapbook-expidxlevels-2011-09-08-13-13.html)
    + [livin-scrapbook | #是也乎# | ZoomQuiet.io](http://blog.zoomquiet.io/livin-scrapbook.html)
    + [zq-chk4scrapbook | #是也乎# | ZoomQuiet.io](http://blog.zoomquiet.io/zq-chk4scrapbook.html)


## changelog

- 2017 增补 README
- 2013 重新发布为 git 仓库
- 2012 发布到 bitbucket
- 2011 整理发布到 code.google
- 2009 工具原型
- 2005 发现 ScrapBook

