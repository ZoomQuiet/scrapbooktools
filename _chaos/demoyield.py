#!/usr/bin/env python
# -*- coding: utf-8 -*-
import types 
DATA= {
'SEQ':{
    "id1":['id11', 'id12']
    ,"id11":['id111']
    ,"id111":['id1111']
    ,"id12":['id21']
    ,"id21":['id211', 'id212']
    }
,'DESC':{'id1':{'title':1,'type':'folder'}
    ,'id11':{'title':11,'type':'folder'}
    ,'id12':{'title':12,'type':'file'}
    ,'id111':{'title':111,'type':'file'}
    ,'id1111':{'title':1111,'type':'file'}
    ,'id21':{'title':21,'type':'folder'}
    ,'id211':{'title':211,'type':'file'}
    ,'id212':{'title':212,'type':'file'}
    }
}

def _exp_all_item(drdf, seq, exp):
   if types.ListType is type(seq):
       for seqid in seq:
           if seqid in drdf['SEQ']:
               yield "<li>%s</ui>" % drdf['DESC'][seqid]['title']
               for x in _exp_all_item(drdf,drdf['SEQ'][seqid],exp):
                   yield x
           else:
               for x in _exp_all_item(drdf,seqid,exp):
                   yield x
   else:
       if seq in drdf['SEQ']:
           yield "<li>%s</ui>" % drdf['DESC'][seq]['title']
           for x in _exp_all_item(drdf,drdf['SEQ'][seq],exp):
               yield x
       else:
           yield "<li>%s</li>" % drdf['DESC'][seq]['title']

if __name__ == '__main__':
   s = list(_exp_all_item(DATA, 'id1', ''))
   print s

