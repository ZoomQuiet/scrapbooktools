# coding : utf-8

import sys,os,string,stat
import time,datetime
# match file name
#import fnmatch
#import calendar,time

# usage ini to cfg all
#import ConfigParser


__version__="fixhtmlexp.py 0.9.1"

class fixhtmlexp:
    """main class zip all done
    """

    def __init__(self):
        """ini all
        """    
        self.dirbook = sys.argv[1]
        self.dirtree = "tree/"
        self.tree = "frame.html"
        self.index = "index.html"
        self.idx = "idx.html"
        self.daylog = "%s"%(time.strftime("%y%m%d %H:%M:%S",time.localtime()))
        #self.ecale = calendar.monthcalendar(ey,em)
        #self.cfg = ConfigParser.ConfigParser()

    def idxit(self):
        """re index the tree of ScrapBook:
            - replace src="./index.html" as src="./idx.html" in frame.html
                - if replaced ,cancel flow ..! judge by SIZE of index.html
            - cp index.html as idx.html
            - cp frame.html as index.html
        """
        root = self.dirbook+self.dirtree 
        #print root
        oldframe = open(root+self.tree).read()
        #print os.stat(root+self.tree)[stat.ST_SIZE]
        print "%s ST_SIZE::%s"%((root+self.index),os.stat(root+self.index)[stat.ST_SIZE])
        if 800 < os.stat(root+self.index)[stat.ST_SIZE]:
            # not replace yet
            #newframe = string.replace(open(root+self.tree).read(),"index.html","idx.html")
            newframe = string.replace(oldframe,"index.html","idx.html")
            #open(root+self.tree,"w").write(newframe)
            open(root+self.idx,"w").write(open(root+self.index).read())
            open(root+self.index,"w").write(newframe)
            #print newframe
        else:
            # cancel replace again
            print "replaced! do nothing..."














    def title(self):
        """readt scrpabook export index.html:
            - fixed Title for zoomquiet.org
        """
        expname = self.dirbook.split("/")[1]
        orgiIdx = open(self.dirbook+self.dirtree+self.index)
        mark = "<title>"
        retit = ""
        for line in orgiIdx:
            if mark in line:
                #print line
                if "</title>" not in line:
                    retit += line
                else:
                    print line
                    newTit='''
                        <title>%s in zoomquiet.org
                        reformat by %s
                        {%s}-ScrapBook</title>
                        '''%(expname,__version__,self.daylog)           
                    print newTit
                    retit += newTit
            else:
                retit += line
        orgiIdx.close()
        open(self.dirbook+self.dirtree+self.index,"w").write(retit)












if __name__ == '__main__':
    """base usage
    """
    fix = fixhtmlexp()
    fix.idxit()
    print ":::And fixed title"
    fix.title()


