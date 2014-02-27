#!/usr/bin/env python
# -*- coding: utf-8 -*-
VERSION = "chkscrap.py v14.02.27"
import os
import sys
import pickle
import types
import time
import shutil
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
        print "\n\t%s() RUNed~ %.5f ms" % (func.__name__, passtime*1000)
        return result
    return cal_time

def exp_level_idx(pathto):
    #print pathto, CF.RDF% pathto, os.path.basename(pathto)
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
                    ,'title':attrs['NS2:title']
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
    output = open('scraotools_%s.pkl' % os.path.basename(pathto) , 'wb')
    pickle.dump(CF.DICTRDF, output)
    #output.close
    return CF.DICTRDF

def chk_data_dir(abspath):
    sub_data = os.listdir("%s/data"% abspath)
    print len(sub_data)
    return sub_data
    
@run_time
def chk_data_ids(expath, drdf):
    rdf = drdf   #pickle.load(open(pkl, 'r'))
    print rdf.keys()
    print rdf['ROOT']
    print len(rdf['DESC'].keys())
    #print rdf['DESC']['item20060616103600']
    rdf_all_id = []
    for r in rdf['DESC']:
        if "folder" == rdf['DESC'][r]['type']:
            pass
        else:
            rdf_all_id.append(r)
    print len(rdf_all_id), type(rdf_all_id)
    ls_sub_data = chk_data_dir(expath)
    print type(ls_sub_data)
    rdf_all_id = [v[4:] for v in rdf_all_id]
    print len(rdf_all_id)#, _all_id[-1:], ls_sub_data[-1]
    #_difference = [v for v in ls_sub_data if v not in _all_id]  
    _difference = set(ls_sub_data).difference(set(rdf_all_id)) # b中有而a中没有的
    print "mes dir is:", len(_difference)
    #print list(_difference)
    for err_dir in _difference:
        abs_err_dir = "%s/data/%s"% (expath, err_dir)
        shutil.rmtree(abs_err_dir)
    #print len(rdf['SEQ'].keys())
    #print rdf['SEQ']['item20070831150256']#.keys()

if __name__ == "__main__":
    if 2 != len(sys.argv):
        print """ %s usage::
$ python /path/2/chkscrap.py /path/2/MyScrapBook/
            |                       +- ScrapBook 收藏入口目录
            +- 指出脚本自身
        """ % VERSION
    else:
        TPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
        MYBOOK = os.path.abspath(sys.argv[1])
        RDFD = exp_level_idx(MYBOOK)
        #exp_root_idx(MYBOOK, RDFD)
        chk_data_ids(MYBOOK, RDFD)
        #chk_data_dir(MYBOOK)
        #exp_root_idx(MYBOOK, RDFD)















