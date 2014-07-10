#!/usr/bin/env python
# -*- coding: utf-8 -*-
VERSION = "expidxlevels.py v11.08.29"
import os
import sys
import pickle
import types
import time
#import traceback
import xml.parsers.expat
#import xml.etree.cElementTree as etree

#from lxml import etree
#from xml.etree.cElementTree import ElementTree
#from rdflib.URIRef import URIRef
#from rdflib.Literal import Literal
#from rdflib.BNode import BNode
#from rdflib.Namespace import Namespace
#from rdflib.constants import TYPE, VALUE
# Import RDFLib's default TripleStore implementation
#from rdflib.TripleStore import TripleStore
#import surf


class Borg():
    '''base http://blog.youxu.info/2010/04/29/borg
        - 单例式配置收集类
    '''
    __collective_mind = {}
    def __init__(self):
        self.__dict__ = self.__collective_mind

    #path
    RDF = "%s/scrapbook.rdf"

    # VANCL esp.
    HTM = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
    	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    	<meta http-equiv="Content-Style-Type" content="text/css">
    	<meta http-equiv="Content-Script-Type" content="text/javascript">
    	<title>{%(bookname)s} index tree exp. As HTML - ScrapBook</title>
    	<link rel="stylesheet" type="text/css" href="./output.css" media="all">

    </head>
    '''
    HTM += '''<body>
    <H3>ZQ's <a href="http://amb.vis.ne.jp/mozilla/scrapbook/">SCRAPBOOK</a> Repo.:{%(bookname)s} root index</H3>
        <table>
        %(body)s
        </table>


    <hr/>
    <div id="poweredby">
    <H4>USAGE</H4>
    <ul>
    <li>Author: <a href="http://about.me/zoom.quiet">Zoom Quiet (zoom.quiet) on about.me</a>
        </li>
    <li>Tools: <a href="https://bitbucket.org/ZoomQuiet/scraptools">ZoomQuiet / scraptools — Bitbucket</a>
        </li>
    <li>Licenses: <a href="http://creativecommons.org/licenses/by-sa/2.5/cn/">CC(by-sa)2.5</a>
        (expect originality licenses of pages)
        </li>
    </ul>

    <b>powered by:</b>
        <a href="http://www.python.org/">Python</a>
        ,<a href="http://amb.vis.ne.jp/mozilla/scrapbook/">SCRAPBOOK</a>
        ,<a href="http://webpages.charter.net/edreamleo/front.html">Leo</a>
        ,<a href="http://www.catb.org/hacker-emblem/">Hacker</a>

     </a>
    </div>

    </body>
    </html>
    '''
    FSET = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN">
    <html>
    <head>
    	<meta http-equiv="Content-Type" Content="text/html;charset=UTF-8">
    	<title>Output {%(seqlevel)s} As HTML Tree - ScrapBook</title>
    </head>
    <frameset cols="200,*">
    	<frame id="side" name="side" src="./%(treeid)s.html">
    	<frame id="main" name="main" src="./main.html">
    </frameset>

    </html>
    '''
    IDX = '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

    <html>

    <head>
    	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    	<meta http-equiv="Content-Style-Type" content="text/css">
    	<meta http-equiv="Content-Script-Type" content="text/javascript">
    	<title>Output As HTML - ScrapBook</title>
    	<link rel="stylesheet" type="text/css" href="./output.css" media="all">
    	<script type="text/javascript" language="JavaScript"><!--
    	function toggle(aID) {
    		var listElt = document.getElementById(aID);
    		listElt.style.display = ( listElt.style.display == "none" ) ? "block" : "none";
    	}
    	function toggleAll(willOpen) {
    		var ulElems = document.getElementsByTagName("UL");
    		for ( var i = 1; i < ulElems.length; i++ ) {
    			ulElems[i].style.display = willOpen ? "block" : "none";
    		}
    	}
    	//--></script>
    </head>
    <!--false -->
    <body onload="toggleAll(true);">
    <UL id="folder-root">
    <li><H3><a href="index.html" target="_top">up {ROOT}</a></H3></li>

    %(treeli)s

    <li><H3><a href="index.html" target="_top">up {ROOT}</a></H3></li>

    </UL>
    </body>
    </html>
    '''

    IS_ROOT = 0
    IS_SEQ = 0
    IS_LI = 0
    IS_DESC = 0

    DICTRDF = {"ROOT":{}
        ,"SEQ":{}
        ,"DESC":{}
        }
    CRTID = ""
    '''
    {"ROOT":{'id':'','li':[]}
    ,"SEQ":{'item...':[]
        ,,,}
    ,"DESC":{'item...':{'id':''
            ,'type':"" # folder||separator
            ,'icon':''
            ,'title':''
            ,'source':''
            ,'chars':''
            ,'comment':''
            }
        ,,,
        }
    }
    '''

# init all cfg. var
CF = Borg()


def run_time(func):
    '''from http://www.oschina.net/code/snippet_74928_3896
        - 简单的计时装饰器
    '''
    def cal_time(*args):
        '''完成目标函式的运行计时
        '''
        start = time.time()
        result = func(*args)
        passtime = time.time() - start
        print "\t\t%s() RUNed~ %.5f ms\n" % (func.__name__, passtime*1000)
        return result
    return cal_time

@run_time
def exp_level_idx(pathto):
    '''解析现有 rdf 为 py 数据对象来快速理解/清查
    '''
    #print pathto, CF.RDF% pathto, os.path.basename(pathto)
    print "%s/scrapbook.rdf"% pathto 
    doc = xmltodict.parse(open("%s/scrapbook.rdf"% pathto, 'r').read())
    #print dir(doc)
    print doc.keys()
    print "RDF:Seq\t\t\t", len(doc['RDF:RDF']['RDF:Seq'])
    print "RDF:Description\t\t", len(doc['RDF:RDF']['RDF:Description'])
    print "NC:BookmarkSeparator\t", len(doc['RDF:RDF']['NC:BookmarkSeparator'])
    XRDF = {'doc':doc
        , 'k2seq':{}
        , 'k2desc':{}
        , 'k2nc':{}
        , 'root':[] #seq['RDF:li']
        }
    # re-index by RDF:about|
    print "keys doc['RDF:RDF']\n\t", doc['RDF:RDF'].keys()
    #print "keys doc['RDF:RDF']['RDF:Seq']", doc['RDF:RDF']['RDF:Seq'].keys()
    #print "keys doc['RDF:RDF']['RDF:Description']", doc['RDF:RDF']['RDF:Description'].keys()
    #print "doc['RDF:RDF']['RDF:Description']", len(doc['RDF:RDF']['RDF:Description'])
    #return None
    for seq in doc['RDF:RDF']['RDF:Seq']:
        if "urn:scrapbook:root" == seq['@RDF:about']:
            XRDF['root'] = seq
        else:
            XRDF['k2seq'][seq['@RDF:about']] = seq
    for desc in doc['RDF:RDF']['RDF:Description']:
        XRDF['k2desc'][desc['@RDF:about']] = desc 
    for nc in doc['RDF:RDF']['NC:BookmarkSeparator']:
        XRDF['k2nc'][nc['@RDF:about']] = nc 

    output = open(CF.PKL % os.path.basename(pathto) , 'wb')
    print output
    #print type(obj.RDF_RDF)
    pickle.dump(XRDF, output)
    return XRDF



    return None   
    
    obj = untangle.parse("%s/scrapbook.rdf"% pathto)
    print dir(obj.RDF_RDF.RDF_Description)
    print "RDF:Seq\t\t\t", len(obj.RDF_RDF.RDF_Seq)
    print "RDF_Description\t\t", len(obj.RDF_RDF.RDF_Description)
    print "NC:BookmarkSeparator\t", len(obj.RDF_RDF.NC_BookmarkSeparator)

    output = open(CF.PKL % os.path.basename(pathto) , 'wb')
    print output
    #print type(obj.RDF_RDF)
    #pickle.dump(obj.RDF_RDF, output)
    return obj.RDF_RDF
    return None    
    
    def start_element(name, attrs):
        #print 'Start element:', name, attrs
        if "RDF:Seq" == name:
            CF.IS_SEQ = 1
            CF.IS_DESC = 0
            if "urn:scrapbook:root" == attrs['RDF:about']:
                #print 'ROOT element:', name, attrs
                CF.IS_ROOT = 1
                CF.DICTRDF['ROOT']['id'] = attrs['RDF:about'].split(":")[-1]
                CF.CRTID = attrs['RDF:about'].split(":")[-1]
                CF.DICTRDF['ROOT']['li'] = []
            else:
                CF.IS_ROOT = 0
                CF.CRTID = attrs['RDF:about'].split(":")[-1]
                CF.DICTRDF['SEQ'][CF.CRTID] = []
        else:
            CF.IS_SEQ = 0
            if "RDF:li" == name:
                CF.IS_DESC = 0
                CF.IS_LI = 1
                if CF.IS_ROOT:
                    CF.DICTRDF['ROOT']['li'].append(attrs['RDF:resource'].split(":")[-1])
                else:
                    CF.DICTRDF['SEQ'][CF.CRTID].append(attrs['RDF:resource'].split(":")[-1])
            elif "RDF:Description" == name:
                CF.IS_DESC = 1
                CF.IS_LI = 0
                CF.CRTID = attrs['RDF:about'].split(":")[-1]
                CF.DICTRDF['DESC'][CF.CRTID] = {
                    'id':attrs['NS2:id']
                    ,'type':attrs['NS2:type']
                    ,'title':attrs['NS2:title']#.encode('utf8')
                    ,'source':attrs['NS2:source']
                    ,'chars':attrs['NS2:chars']
                    ,'icon':attrs['NS2:icon']
                    ,'comment':attrs['NS2:comment']
                    }







    def end_element(name):
        if "RDF:Seq" == name:
            if CF.IS_ROOT:
                CF.IS_ROOT = 0
            else:
                pass
    px = xml.parsers.expat.ParserCreate()
    px.StartElementHandler = start_element
    px.EndElementHandler = end_element
    px.Parse(open(CF.RDF % pathto).read(), 1)
    output = open(CF.PKL % os.path.basename(pathto) , 'wb')
    pickle.dump(CF.DICTRDF, output)
    #output.close
    return CF.DICTRDF


'''
{'ROOT':[item,,,]
        , 'SEQ':{'itemID':[item,,,],,,}
        , 'DESC':['itemID':{'属性':'属性值',,},,,]
    }
    ROOT 结点 -> [SEQ|DESC]
        SEQ 都是目录;
        DESC 都是最终叶子;
    
'''
@run_time
def exp_root_idx(expath, drdf):
    rdf = drdf   #pickle.load(open(pkl, 'r'))
    bookname = os.path.basename(expath)
    htm = ""
    count = 0
    loops = 0
    for rootseq in rdf['ROOT']['li']:
        loops += 1
        if 0 == (loops % 2):
            htm += '<tr><td>%s</td></tr>\n'% _seq_info(rdf, rootseq)
        else:
            htm += '<tr class="odd"><td>%s</td></tr>\n'% _seq_info(rdf, rootseq)
        count += exp_sub_idx(expath, rdf, rootseq)
    print "collected pages == ", count
    body = htm.encode('utf8')
    html = CF.HTM % locals()
    #open("%s/tree/root-idx.html"% expath, 'w').write(html.encode('utf8'))
    open("%s/tree/index.html"% expath, 'w').write(html)
def exp_sub_idx(expath, drdf, seqid):
    rdf = drdf   #pickle.load(open(pkl, 'r'))
    bookname = os.path.basename(expath)    
    body = "<tr><td><H3><a href='index.html'>back ROOT index</a></H3></td></tr>"
    tot = 0
    if seqid in rdf['SEQ']:
        for subseq in rdf['SEQ'][seqid]:
            body += '<tr><td>%s</td></tr>\n' % _seq_info(rdf, subseq)
            if subseq in rdf['SEQ']:
                tot += exp_if_tree(expath, rdf, seqid, subseq)
    return tot

def exp_if_tree(expath, drdf, crtseq, seqid):
    rdf = drdf   #pickle.load(open(pkl, 'r'))
    bookname = os.path.basename(expath)
    treeli = ""
    ulis = list(_uli_all_item(rdf, seqid))
    treeli = "\n".join(ulis)
    upback = "item%s-idx.html" % drdf['DESC'][crtseq]['id']
    html = CF.IDX % locals()
    open("%s/tree/%s-tree.html"% (expath, seqid),'w').write(html.encode('utf8'))
    treeid = "%s-tree" % seqid
    seqlevel = drdf['DESC'][seqid]['title']
    html = CF.FSET % locals()
    open("%s/tree/%s-frameset.html"% (expath, seqid),'w').write(html.encode('utf8'))
    return len(ulis)

def _uli_all_item(drdf, seq):
    if types.ListType is type(seq):
        for seqid in seq:
            if seqid in drdf['SEQ']:
                yield '''<LI><a class="folder">
                <img src="./folder.png" width="16" height="16" alt="">
                %s</a><UL>''' % drdf['DESC'][seqid]['title']
                for ul in _uli_all_item(drdf, drdf['SEQ'][seqid]):
                    yield ul
                yield "</UL></LI>"
            else:
                for li in _uli_all_item(drdf, seqid):
                    yield li
    else:
        if seq in drdf['SEQ']:
            yield "<LI>%s<UL>" % drdf['DESC'][seq]['title']
            for ul in _uli_all_item(drdf, drdf['SEQ'][seq]):
                yield ul    #"</ul></li>"
            yield "</UL></LI>"
        else:
            if seq in drdf['DESC']:
                if 'folder' == drdf['DESC'][seq]['type']:
                    yield '''<LI><a class="folder">
                    <img src="./folder.png" width="16" height="16" alt="">
                    %s</a><UL>''' % drdf['DESC'][seq]['title']
                elif 'note' == drdf['DESC'][seq]['type']:
                    yield '''<LI>
                    <a href="../data/%s/index.html" target="main" class="item">
                    <img src="./treenote.png" width="16" height="16" alt="">
                    %s</a><UL>''' % (drdf['DESC'][seq]['id']
                        ,drdf['DESC'][seq]['title'])
                else:
                    yield '''<LI>
                    <a href="../data/%s/index.html" target="main" class="item">
                    <img src="./treeitem.png" width="16" height="16" alt="">
                    %s</a></LI>''' % (drdf['DESC'][seq]['id']
                        ,drdf['DESC'][seq]['title'])
            else:
                yield "<HR/>"
def _seq_info(rdf, seqid):
    exphtm = ""
    if seqid in rdf['SEQ']:
        exphtm += _desc_info(rdf, seqid, is_root=True)
        for subid in rdf['SEQ'][seqid]:
            exphtm += _desc_info(rdf, subid)
    elif seqid in rdf['DESC']:
        exphtm += _desc_info(rdf, seqid)
    else:
        #print "is NC:BookmarkSeparator"
        exphtm += '' 
    return exphtm
def _desc_info(rdf, rdfid, is_root=False):
    #print rdfid
    if rdfid in rdf['DESC']:
        itemtitle = rdf['DESC'][rdfid]['title']
        tipid = rdf['DESC'][rdfid]['id']
        if rdfid in rdf['ROOT']['li']:
            if 'folder' == rdf['DESC'][rdfid]['type']:
                return '<span id="rootitem"><b>{%s}</b></span>' % rdf['DESC'][rdfid]['title']
            else:
                return '''<span id="rootitem">
                <b><a href="../data/%s/index.html">{%s}</a></b>
                </span>''' % (rdf['DESC'][rdfid]['id']
                    ,rdf['DESC'][rdfid]['title'])
        elif 'folder' == rdf['DESC'][rdfid]['type']:
            if is_root:
                return '''<span id="rootitem">
                <a title="%(tipid)s" href="item%(tipid)s-frameset.html">
                <b>[%(itemtitle)s]</b>
                </a></span>'''% locals() 
            else:
                return '''<span id="item" class="hadsubitems">
                <a title="%(tipid)s" href="item%(tipid)s-frameset.html">
                [%(itemtitle)s]
                </a></span>'''% locals() 
        else:       
            return '''<span id="item" class="idx-%(tipid)s">
            ;<a href="../data/%(tipid)s/index.html" title="%(itemtitle)s" class="jqactshow">%(itemtitle)s</a>
            </span>'''% locals()
    else:
        #print "is NC:BookmarkSeparator"
        return ""

if __name__ == "__main__":
    if 2 != len(sys.argv):
        print """ %s 将指定ScrapBook 的输出树图分解为一批小索引 usage::
$ python /path/2/expidxlevels.py /path/2/MyScrapBook/
            |                       +- ScrapBook 收藏入口目录
            +- 指出脚本自身
        """ % VERSION
    else:
        TPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
        MYBOOK = os.path.abspath(sys.argv[1])
        RDFD = exp_level_idx(MYBOOK)
        exp_root_idx(MYBOOK, RDFD)















