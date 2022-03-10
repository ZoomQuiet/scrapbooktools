#!/usr/bin/env python
# -*- coding: utf-8 -*-
VERSION = "chkscrap.py v14.07.08"
import os
import sys
import pickle
import types
import time
import shutil
#import traceback
import xml.parsers.expat
#import xml.etree.cElementTree as etree
#   140708 try click
import click

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
    PKL = '_chaos/scraotools_%s.pkl'
    TREE = '_chaos/tree4_%s.txt'

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

def chk_data_dir(abspath):
    sub_data = os.listdir("%s/data"% abspath)
    print "\t data/dirs : %s"% len(sub_data)
    return sub_data
@run_time
def exp_level_idx(pathto):
    '''解析现有 rdf 为 py 数据对象来快速理解/清查
    {'ROOT':[item,,,]
        , 'SEQ':{'itemID':[item...],,,}
        , 'DESC':[item,,,]
    }
    ROOT 结点 -> [SEQ|DESC]
        SEQ 都是目录;
        DESC 都是最终叶子;
    '''
    #print pathto, CF.RDF% pathto, os.path.basename(pathto)
    def start_element(name, attrs):
        #print 'Start element:', name, attrs
        if name == "RDF:Seq":
            CF.IS_SEQ = 1
            CF.IS_DESC = 0
            if attrs['RDF:about'] == "urn:scrapbook:root":
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
            if name == "RDF:li":
                CF.IS_DESC = 0
                CF.IS_LI = 1
                if CF.IS_ROOT:
                    CF.DICTRDF['ROOT']['li'].append(attrs['RDF:resource'].split(":")[-1])
                else:
                    CF.DICTRDF['SEQ'][CF.CRTID].append(attrs['RDF:resource'].split(":")[-1])
            elif name == "RDF:Description":
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
        if name == "RDF:Seq" and CF.IS_ROOT:
            CF.IS_ROOT = 0
    px = xml.parsers.expat.ParserCreate()
    px.StartElementHandler = start_element
    px.EndElementHandler = end_element
    px.Parse(open(CF.RDF % pathto).read(), 1)
    output = open(CF.PKL % os.path.basename(pathto) , 'wb')
    pickle.dump(CF.DICTRDF, output)
    #output.close
    return CF.DICTRDF

@run_time
def chk_data_ids(expath, drdf):
    rdf = drdf   #pickle.load(open(pkl, 'r'))
    #print rdf.keys()
    #print "\t rdf.keys :\t %s"% rdf.keys()
    #print rdf['ROOT']
    print "\t DESC nodes : %s"% len(rdf['DESC'].keys())
    #print rdf['DESC']['item20060616103600']
    rdf_all_id = []
    for r in rdf['DESC']:
        if "folder" == rdf['DESC'][r]['type']:
            pass
        else:
            rdf_all_id.append(r)
    print "\t rdf nodes:", len(rdf_all_id), type(rdf_all_id)
    ls_sub_data = chk_data_dir(expath)
    #print "\t type(ls_sub_data)", type(ls_sub_data)
    rdf_all_id = [v[4:] for v in rdf_all_id]
    #print len(rdf_all_id)#, _all_id[-1:], ls_sub_data[-1]
    #_difference = [v for v in ls_sub_data if v not in _all_id]  
    _difference = set(ls_sub_data).difference(set(rdf_all_id)) # b中有而a中没有的
    print "losted dir :", len(_difference)
    #print list(_difference)
    for err_dir in _difference:
        abs_err_dir = "%s/data/%s"% (expath, err_dir)
        shutil.rmtree(abs_err_dir)
    #print len(rdf['SEQ'].keys())
    #print rdf['SEQ']['item20070831150256']#.keys()
# 解决写文件 'ascii' codec can't encode characters 问题
# base http://blog.csdn.net/zuyi532/article/details/8851316
reload(sys)  
sys.setdefaultencoding('utf8')   
# 全局变量
exp_items = []  # 实际输出节点对象
loop_safe = 5   # 递归安全深度
exp_txt = ""    # 输出文本桟

@run_time
def exp_rdf_tree(expath, drdf):
    '''怀疑有很多根本没有出现在树中的结点!
    '''
    rdf = drdf
    print "\t DESC nodes : %s"% len(rdf['DESC'].keys())
    cnt = rdf['DESC']['item20100326204458']['title']
    #print rdf['SEQ']['item20120823113510']
    deepl = 0
    for r in rdf['ROOT']['li']:
        exp_items.append(r)
        _exp_txt_tree(exp_txt, deepl, r, drdf)
    #casename = os.path.basename(expath)
    #open(CF.TREE % casename, 'w').write(exp_txt)
    print "\t exp_items: ", len(exp_items)
def _exp_txt_tree(exp_txt, deepl, node, drdf):
    if deepl > loop_safe:
        return None
    rdf = drdf
    r = node
    pre = ".." * deepl
    if r in rdf['DESC'].keys():
        exp_items.append(r)
        if '' == rdf['DESC'][r]['source']:
            print "%s%s D %s"% (pre, r, rdf['DESC'][r]['title'])
        else:
            print "%s%s c %s"% (pre, r, rdf['DESC'][r]['title'])

    if r in rdf['SEQ'].keys():
        #print rdf['SEQ'][r]
        exp_items.append(r)
        for l in rdf['SEQ'][r]:
            _exp_txt_tree(exp_txt, deepl+1, l, drdf)
    else:
        pass
        #print "\t one line---"
    return deepl+1




@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj['DEBUG'] = debug

@cli.command()
@click.pass_context
def sync(ctx):
    print('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))
    print('syncing...')
if __name__ == "__main__":
    cli(obj={})
    '''
    if 2 != len(sys.argv):
        print """ %s 检查 ScrapBook 仓库目录
    usage::
    $ python /path/2/chkscrap.py /path/2/MyScrapBook/
            |                       +- ScrapBook 收藏入口目录
            +- 指出脚本自身
        """ % VERSION
    else:
        TPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
        MYBOOK = os.path.abspath(sys.argv[1])
        #REPO_NAME = os.path.basename(MYBOOK)
        
        RDFD = exp_level_idx(MYBOOK)
        #print CF.PKL % sys.argv[1]
        #RDFD = pickle.load(open(CF.PKL % MYBOOK, 'r'))
        #chk_data_ids(MYBOOK, RDFD)
        #   exp_root_idx(MYBOOK, RDFD)
        #   chk_data_dir(MYBOOK)
        exp_rdf_tree(MYBOOK, RDFD)


    '''
    













