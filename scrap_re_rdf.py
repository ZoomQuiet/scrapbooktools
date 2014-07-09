#!/usr/bin/env python
# -*- coding: utf-8 -*-
VERSION = "scrap_re_rdf.py v14.02.27"
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

    RDF_ROOT = '''<?xml version="1.0"?>
    <RDF:RDF xmlns:NS2="http://amb.vis.ne.jp/mozilla/scrapbook-rdf#"
             xmlns:NC="http://home.netscape.com/NC-rdf#"
             xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      %(rdf_items)s
    </RDF:RDF>
    '''

    RDF_SEQ_ROOT = '''<RDF:Seq RDF:about="urn:scrapbook:root">
    %(seq_lis)s  </RDF:Seq>
    '''
    RDF_SEQ_UL = '''<RDF:Seq RDF:about="urn:scrapbook:%(rdf_about)s">
    %(seq_lis)s  </RDF:Seq>
    '''
    RDF_SEQ_LI = '''    <RDF:li RDF:resource="urn:scrapbook:%(seq_res)s"/>
    '''

    RDF_DESC = '''<RDF:Description RDF:about="urn:scrapbook:%(rdf_about)s"
                    NS2:id="%(rdf_id)s"
                    NS2:type="%(rdf_type)s"
                    NS2:title="%(rdf_title)s"
                    NS2:chars="%(rdf_chars)s"
                    NS2:icon="%(rdf_icon)s"
                    NS2:source="%(rdf_scource)s"
                    NS2:comment="%(rdf_comment)s" />
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
def rebuild_rdf(expath, drdf):
    rdf = drdf   #pickle.load(open(pkl, 'r'))
    print rdf.keys()
    seq_lis = ""
    ROOT_KEYS = rdf['ROOT']['li']
    SEQ_KEYS = rdf['SEQ'].keys()
    DESC_KEYS = rdf['DESC'].keys()
    for r in ROOT_KEYS:
        #print r
        seq_res = r 
        seq_lis += CF.RDF_SEQ_LI% locals()

    rdf_items = CF.RDF_SEQ_ROOT% locals()

    for r in ROOT_KEYS:
        if r in SEQ_KEYS:
            rdf_about = r
            seq_lis = ""
            for sub_r in rdf['SEQ'][r]:
                seq_res = sub_r 
                seq_lis += CF.RDF_SEQ_LI% locals()

            crt_seq = CF.RDF_SEQ_UL% locals()
            rdf_items += crt_seq


    #rdf['ROOT']['li']
    for r in SEQ_KEYS:
        if r not in ROOT_KEYS:
            #in SEQ_KEYS
            rdf_about = r
            #print r
            seq_lis = ""
            for sub_r in rdf['SEQ'][r]:
                seq_res = sub_r 
                seq_lis += CF.RDF_SEQ_LI% locals()
            #print seq_lis

            #return None
            crt_seq = CF.RDF_SEQ_UL% locals()
            rdf_items += crt_seq
            #print rdf_items

        #return None



    for r in DESC_KEYS:    
        rdf_about = r
        rdf_id = rdf['DESC'][r]['id']
        rdf_type = rdf['DESC'][r]['type']
        rdf_title = rdf['DESC'][r]['title']
        rdf_chars = rdf['DESC'][r]['chars']
        rdf_icon = rdf['DESC'][r]['icon']
        rdf_scource = rdf['DESC'][r]['source']
        rdf_comment = rdf['DESC'][r]['comment']
        
        crt_dec = CF.RDF_DESC% locals()
        rdf_items += crt_dec


    re_rdf = CF.RDF_ROOT% locals()
    #print re_rdf
    open("scrapbook.rdf",'w').write(re_rdf.encode('utf-8'))
    #print 'item20091113232313' in rdf['SEQ'].keys()#['item20091113232313']
    #print rdf['SEQ']['item20070527155735']
    #print len(rdf['ROOT']['li'])
    
    


    
    

if __name__ == "__main__":
    if 2 != len(sys.argv):
        print """ %s 重构 rdf 索引数据库 usage::
$ python /path/2/scrap_re_rdf.py /path/2/MyScrapBook/
            |                       +- ScrapBook 收藏入口目录
            +- 指出脚本自身
        """ % VERSION
    else:
        TPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
        MYBOOK = os.path.abspath(sys.argv[1])
        RDFD = exp_level_idx(MYBOOK)
        #exp_root_idx(MYBOOK, RDFD)
        rebuild_rdf(MYBOOK, RDFD)
        #chk_data_dir(MYBOOK)
        #exp_root_idx(MYBOOK, RDFD)















