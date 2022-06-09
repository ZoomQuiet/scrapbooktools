#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''主要检查行为:
-D 是否加载上次已经分析的对象树
-diff 对比 rdf 和 目录 的节点数量
-exp 输出 rdf 显示节点树
-chaos 清查未显示节点列表
-rm|mv 清除/移动 未显示节点目录集
'''

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
#   140709 ty sh del dir, and others for rebuild rdf
from sh import cp
from sh import rm
from sh import mv
from sh import ls
from sh import wc
#import untangle
import xmltodict
import progressbar

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
    IDPRE = "urn:scrapbook:item%s"
    RDF = "%s/scrapbook.rdf"
    RERDF = '_chaos/scrapbook_%s.rdf'
    PKL = '_chaos/scraptools_%s.pkl'
    TREE = '_chaos/tree4_%s.txt'
    STUFF = '_stuff/'

    TPL_BODY = '''<?xml version="1.0"?>
    <RDF:RDF xmlns:NS2="http://amb.vis.ne.jp/mozilla/scrapbook-rdf#"
             xmlns:NC="http://home.netscape.com/NC-rdf#"
             xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    %(rdf_body)s
    </RDF:RDF>
    '''

    TPL_ROOT = '''<RDF:Seq RDF:about="urn:scrapbook:root">
        %(rdf_li)s
      </RDF:Seq>
    '''
    TPL_SEQ = '''<RDF:Seq RDF:about="urn:scrapbook:%(rdf_item)s">
        %(rdf_li)s
      </RDF:Seq>
    '''
    TPL_LI = '''
    <RDF:li RDF:resource="urn:scrapbook:%(rdf_item)s"/>
    '''

    TPL_FOLDER = '''
    <RDF:Description RDF:about="urn:scrapbook:%(rdf_item)s"
            NS2:type="folder"
            NS2:id="%(rdf_id)s"
            NS2:title="%(rdf_title)s"
            NS2:chars=""
            NS2:icon=""
            NS2:source=""
            NS2:comment="" />
    '''
    TPL_NOTE = '''
    <RDF:Description RDF:about="urn:scrapbook:%(rdf_item)s"
            NS2:type="note"
            NS2:id="%(rdf_id)s"
            NS2:title="%(rdf_title)s"
            NS2:chars="UTF-8"
            NS2:comment=""
            NS2:icon=""
            NS2:source=""/>
    '''
    # type 为空或是"marked"
    TPL_URI = '''
    <RDF:Description RDF:about="urn:scrapbook:%(rdf_item)s"
            NS2:type="%(rdf_type)s"
            NS2:id="%(rdf_id)s"
            NS2:title="%(rdf_title)s"
            NS2:comment="%(rdf_comment)s"
            NS2:icon="%(rdf_icon)s"
            NS2:source="%(rdf_source)s" 
            NS2:chars="UTF-8" />
    '''

    TPL_NC = '''
    <NC:BookmarkSeparator RDF:about="urn:scrapbook:%(rdf_item)s"
            NS2:type="separator"
            NS2:id="%(rdf_id)s"
            NS2:title=""
            NS2:chars=""
            NS2:comment=""
            NS2:icon=""
            NS2:source="" />
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
            ,'type':"" # folder|separator|note
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
def chk_data_dir(abspath):
    sub_data = os.listdir("%s/data"% abspath)
    print "\t data/dirs : %s"% len(sub_data)
    return sub_data
@run_time
def _load_pkl(REPO_NAME):
    print CF.PKL % REPO_NAME
    XRDF = pickle.load(open(CF.PKL % REPO_NAME, 'r'))
    print XRDF.keys()
    print "RDF:ROOT\t", len(XRDF['root']['RDF:li'])
    #print RDFD['root']
    print "RDF:Seq\t\t\t", len(XRDF['k2seq'].keys())
    print "RDF:Description\t\t", len(XRDF['k2desc'].keys())
    print "NC:BookmarkSeparator\t", len(XRDF['k2nc'])
    
    return XRDF


    
@run_time
def exp_level_idx(pathto):
    '''解析现有 rdf 为 py 数据对象来快速理解/清查
    '''
    #print pathto, CF.RDF% pathto, os.path.basename(pathto)
    print "%s/scrapbook.rdf"% pathto 
    doc = xmltodict.parse(open("%s/scrapbook.rdf"% pathto, 'r').read())
    #print dir(doc)
    '''
    for seq in doc['RDF:RDF']['RDF:Seq']:
        if 'urn:scrapbook:search' == seq['@RDF:about']:
            print dir(seq)
            print seq.keys()
            print "son of urn:scrapbook:search:", len(seq['RDF:li'])
            seq.pop('RDF:li')
            break



    '''
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
    # re-index for KV points
    print "keys doc['RDF:RDF']\n\t", doc['RDF:RDF'].keys()
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


'''
#   140711 Alert!
<RDF:Seq RDF:about="urn:scrapbook:search">
</RDF:Seq>


{'ROOT':[item,,,]
        , 'SEQ':{'itemID':[item,,,],,,}
        , 'DESC':['itemID':{'属性':'属性值',,},,,]
    }
    ROOT 结点 -> [SEQ|DESC]
        SEQ 都是目录;
        DESC 都是最终叶子;
    
'''
@run_time
def rm_chaos_search(REPO_NAME, XRDF):
    """Must empty as:
    <RDF:Seq RDF:about="urn:scrapbook:search">
    </RDF:Seq>
    """
    RDFD = XRDF['doc']['RDF:RDF']
    for seq in RDFD['RDF:Seq']:
        if 'urn:scrapbook:search' == seq['@RDF:about']:
            print "son of urn:scrapbook:search:", len(seq['RDF:li'])
            seq.pop('RDF:li')
            break
    open(CF.RERDF % REPO_NAME, "w").write(
        xmltodict.unparse(XRDF['doc'], pretty=True))
    return None
    
_RIGHT_NODES = [] # collect all showing nodes: dir/note/line/page
@run_time
def re_xmltodict_rdf(REPO_NAME, XRDF):
    """usage xmltodict check hided chaos nodes
        and re-build tiny rdf
        for ScrapBook reload
    """
    print XRDF.keys()
    RDFD = XRDF['doc']['RDF:RDF']
    K2SEQ = XRDF['k2seq']
    K2DESC = XRDF['k2desc']
    K2NC = XRDF['k2nc']
    print "RDF:Seq\t\t\t", len(RDFD['RDF:Seq'])
    print "RDF:Description\t\t", len(RDFD['RDF:Description'])
    print "NC:BookmarkSeparator\t", len(RDFD['NC:BookmarkSeparator'])
    print "\tK2DESC\t", len(K2DESC)
    ROOT = XRDF['root']
    #print ROOT['RDF:li']
    #print "\t K2NC:", K2NC['urn:scrapbook:item20091118105509']
    for li in ROOT['RDF:li']:
        #print "\t ROOT here walk out all rights nodes!"
        _walk_rdf_tree(exp_txt, 1, li, XRDF)

    print "\t _RIGHT_NODES:", len(_RIGHT_NODES)
    RIGHT_NODES = list(set(_RIGHT_NODES))
    print "\t RIGHT_NODES:", len(RIGHT_NODES)
    RDF_DESC = XRDF['doc']['RDF:RDF']['RDF:Description']
    K2DESC = XRDF['k2desc']
    #print "id->RDF_DEC", id(RDF_DESC)
    #print "id->XRDF['doc']...", id(XRDF['doc']['RDF:RDF']['RDF:Description'])
    max_action = len(RDF_DESC)# - len(RIGHT_NODES)
    #(end=max_action, width=79)
    opt_pbar = {'end':max_action, 'width':64
        , 'fill': '>'
        }
    pbar = progressbar.AnimatedProgressBar(**opt_pbar)
    ccount = 0
    for i in RDF_DESC:
        crt_ID = i['@RDF:about']
        if crt_ID not in RIGHT_NODES:
            ccount += 1
            #print RDF_DESC.index(i)
            K2DESC.pop(crt_ID)
            RDF_DESC.pop(RDF_DESC.index(i))

            pbar+1
            pbar.show_progress()

    print "\nchaos notes:\t", ccount
    print "clean DESC:\t", len(RDF_DESC)
    if "CTIME" not in XRDF.keys():
        XRDF['CTIME'] = 2
    else:
        XRDF['CTIME'] = XRDF['CTIME'] + 1
    # re-writed as .pkl
    _PKL = CF.PKL % REPO_NAME
    print(rm("-fv", _PKL))

    output = open(_PKL , 'wb')
    print output
    pickle.dump(XRDF, output)

    #return None
    if 0 == ccount:
        # finshed cleanning
        open(CF.RERDF % REPO_NAME, "w").write(
            xmltodict.unparse(XRDF['doc'], pretty=True))
        print CF.RERDF % REPO_NAME
    else:
        # try more time
        #XRDF = _load_pkl(REPO_NAME)
        print ">"*13, "reTRY cleanning", XRDF['CTIME']
        # call self try again
        re_xmltodict_rdf(REPO_NAME, XRDF)
















    return None

def _walk_rdf_tree(exp_txt, deepl, crt_node, XRDF):
    """base pointed node, try dig all of son nodes
    - all start node must be RDF:Seq
    - if not , means end dig do others matter
    """
    if deepl > loop_safe:
        return None
    RDFD = XRDF['doc']['RDF:RDF']
    K2SEQ = XRDF['k2seq']
    K2DESC = XRDF['k2desc']
    K2NC = XRDF['k2nc']
    if '@RDF:resource' in crt_node.keys():
        # Seq|Li
        crt_id = crt_node['@RDF:resource']
    else:   
        # DESC|NC
        crt_id = crt_node['@RDF:about']
    # 记录了包含目录以及其它所有有效的节点
    _RIGHT_NODES.append(crt_id)
    # for recursion must test all cases

    if crt_id in K2SEQ.keys():
        # means contents: note/line/page
        #_print_tree_node(deepl, crt_id, K2DESC)
        if 'RDF:li' not in K2SEQ[crt_id].keys():
            """<RDF:Seq RDF:about="urn:scrapbook:item20120321212141">
            </RDF:Seq>
            类似的空目录情况....
            直接输出目录名就好
            """
        elif len(K2SEQ[crt_id]['RDF:li']) == 1:
            _walk_rdf_tree(exp_txt
                , deepl+1
                , K2SEQ[crt_id]['RDF:li']
                , XRDF)
            _RIGHT_NODES.append(K2SEQ[crt_id]['RDF:li']['@RDF:resource'])

        else:
            #print type(K2SEQ[crt_id]['RDF:li'])
            #print K2SEQ[crt_id]['RDF:li']
            for li in K2SEQ[crt_id]['RDF:li']:
                #print "K2SEQ[crt_id]>RDF:Li", li
                _walk_rdf_tree(exp_txt
                    , deepl+1
                    , li
                    , XRDF)
                _RIGHT_NODES.append(li['@RDF:resource'])

    return deepl+1, exp_txt


def _print_tree_node(deepl, crt_id, K2DESC):
    if crt_id in K2DESC:
        n_type = K2DESC[crt_id]['@NS2:type']
        show_type = "c"
        if "folder" == n_type:
            show_type = "D"
        elif "note" == n_type:
            show_type = "N"
        else:
            pass
        print "%s %s %s %s"% (".."*deepl
            , show_type
            , crt_id.split(':')[-1]
            , K2DESC[crt_id]['@NS2:title']
            )
    else:
        print "~"*42




@run_time
def mv_chaos_data(REPO_NAME, XRDF):
    """对比 data/ 目录和有效节点 ID
    - mv 文章目录到指定备案目录 CF.STUFF
    """
    K2DESC = XRDF['k2desc']
    RDF_DESC = XRDF['doc']['RDF:RDF']['RDF:Description']
    _AIM_DRI = "%s/data"% REPO_NAME
    #print _AIM_DRI
    #data_ls = ls("-1", _AIM_DRI)
    #data_li = data_ls.stdout.split()
    data_li = os.listdir(_AIM_DRI)
    print len(data_li), "\t<-- %s sub dirs"% _AIM_DRI
    #print len(RDF_DESC), "\t<-- doc['RDF:RDF']['RDF:Description']"
    #print len(K2DESC.keys()), "\t<-- K2DESC.keys()"
    _K4DESC = []
    for i in K2DESC.keys():
        _K4DESC.append(K2DESC[i]['@RDF:about'][-14:])
    #print len(_K4DESC), "\t<-- _K4DESC"
    #return None
    max_action = len(data_li)
    #import progressbar
    #(end=max_action, width=79)
    opt_pbar = {'end':max_action, 'width':64
        , 'fill': '>'
        }
    pbar = progressbar.AnimatedProgressBar(**opt_pbar)
    count = 0
    for li in data_li:
        #_id = CF.IDPRE % li
        #return None
        pbar+1
        pbar.show_progress()
        if li not in _K4DESC:   #K2DESC.keys():
            count += 1
            _SRC = "%s/%s"% (_AIM_DRI, li)
            #mv(_SRC, CF.STUFF)
            cp("-rf", _SRC, CF.STUFF)
            rm("-rf", _SRC)
            #print "mv -v %s %s"% (_SRC, CF.STUFF)
            #break
    print "\n\tmv %s dir into %s"% (count, CF.STUFF)
    print "means keep %s dir"% (len(data_li) - count)
    print ">>> ls -1 %s|wc -l"% _AIM_DRI
    print(wc(ls("-1", _AIM_DRI), "-l"))
    return None


@run_time
def chk_data_ids(expath, drdf):
    rdf = drdf   #pickle.load(open(pkl, 'r'))
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
    rdf_all_id = [v[4:] for v in rdf_all_id]
    #_difference = [v for v in ls_sub_data if v not in _all_id]  
    _difference = set(ls_sub_data).difference(set(rdf_all_id)) # b中有而a中没有的
    print "losted dir :", len(_difference)
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
exp_txt = []    # 输出文本桟

@run_time
def exp_rdf_tree(expath, drdf):
    '''怀疑有很多根本没有出现在树中的结点!
    '''
    rdf = drdf
    #print rdf['DESC']['item20100817230519']
    deepl = 0
    for r in rdf['ROOT']['li']:
        exp_items.append(r)
        crt_deep, crt_tree = _exp_txt_tree(exp_txt, deepl, r, drdf)
    casename = os.path.basename(expath)
    print "\t tree_nodes: ",len(exp_txt)
    open(CF.TREE % casename, 'w').write("\n".join(exp_txt))
    print "\t exp_items: ", len(exp_items)
    print "\t dirs: ", len(exp_items) - len(exp_txt)
    
    print "\t DESC : %s"% len(rdf['DESC'].keys())
    #_diff_show_tree(expath, exp_items, drdf)


def _diff_show_tree(expath, show_items, drdf):
    rdf = drdf
    showed = list(set(show_items))
    chaos = []
    for node in rdf['DESC'].keys():
        if node not in showed:
            chaos.append(rdf['DESC'][node])
    print "\t chaos:", len(chaos)
    print "\t 有效:", len(rdf['DESC'].keys())-len(chaos)
    for c in chaos:
        del_dir = "%s/data/%s"% (expath, c['id'])
        print(rm("-Rfv", del_dir))
        #os.removedirs(del_dir)
        #break
def _exp_txt_tree(exp_txt, deepl, node, drdf):
    if deepl > loop_safe:
        return None
    rdf = drdf
    r = node
    pre = ".." * deepl
    if r in rdf['DESC'].keys():
        exp_items.append(r)
        dir_type = rdf['DESC'][r]['type']
        #print "%s%s %s %s"% (pre, r, dir_type, rdf['DESC'][r]['title'])
        exp_txt.append("%s%s %s %s"% (pre, r, dir_type, rdf['DESC'][r]['title']))
    # 可能重ID ?
    if r in rdf['SEQ'].keys():
        #print rdf['SEQ'][r]
        exp_items.append(r)
        for l in rdf['SEQ'][r]:
            _exp_txt_tree(exp_txt, deepl+1, l, drdf)
    else:
        if r in rdf['DESC'].keys():
            print rdf['DESC'][r]['type']
        else:
            print r
            return None
            #print "\t NC:BookmarkSeparator",r
            #exp_items.append(r)
        #print "\t one line---"
    return deepl+1, exp_txt






VERSION = "chkscrap.py v14.07.08"
@click.group()
@click.version_option()
def cli():
    """检查 ScrapBook 仓库目录
    """
    print('V 14.7.8.20')

@cli.group()
def ship():
    """Manages ships."""


@ship.command('new')
@click.argument('name')
def ship_new(name):
    """Creates a new ship."""
    click.echo('Created ship %s' % name)


@ship.command('move')
@click.argument('ship')
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.option('--speed', metavar='KN', default=10,
              help='Speed in knots.')
def ship_move(ship, x, y, speed):
    """Moves SHIP to the new location X,Y."""
    click.echo('Moving ship %s to %s,%s with speed %s' % (ship, x, y, speed))


@ship.command('shoot')
@click.argument('ship')
@click.argument('x', type=float)
@click.argument('y', type=float)
def ship_shoot(ship, x, y):
    """Makes SHIP fire to X,Y."""
    click.echo('Ship %s fires to %s,%s' % (ship, x, y))


@cli.group('mine')
def mine():
    """Manages mines."""


@mine.command('set')
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.option('ty', '--moored', flag_value='moored',
              default=True,
              help='Moored (anchored) mine. Default.')
@click.option('ty', '--drifting', flag_value='drifting',
              help='Drifting mine.')
def mine_set(x, y, ty):
    """Sets a mine at a specific coordinate."""
    click.echo('Set %s mine at %s,%s' % (ty, x, y))


@mine.command('remove')
@click.argument('x', type=float)
@click.argument('y', type=float)
def mine_remove(x, y):
    """Removes a mine at a specific coordinate."""
    click.echo('Removed mine at %s,%s' % (x, y))


if __name__ == "__main__":
    #cli(obj={})

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
        REPO_NAME = os.path.basename(MYBOOK)
        #print REPO_NAME
        #XRDF = exp_level_idx(MYBOOK)
        XRDF = _load_pkl(REPO_NAME)
        rm_chaos_search(REPO_NAME, XRDF)
        #re_xmltodict_rdf(REPO_NAME, XRDF)
        #mv_chaos_data(REPO_NAME, XRDF)
        #   chk_data_ids(MYBOOK, XRDF)
        #   exp_root_idx(MYBOOK, XRDF)
        #   chk_data_dir(MYBOOK)
        #exp_rdf_tree(MYBOOK, XRDF)

    
    













