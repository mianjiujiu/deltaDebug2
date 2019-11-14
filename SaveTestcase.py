
import sys, os
import string
import re
import time
import popen2
import sqlite3
import cStringIO
import gccunions
import mmapunions


# Own modules
from StateGDB import StateGDB
from DB import DB3
import check
from versionsDebug import versionsDebug


#-------
class Testcase:
    def __init__(self, debuggee, invocation, 
                 union_table = None, filter = None):
        self.debuggee = debuggee
        if isinstance(invocation, type([])):
            self.invocation = invocation
        else:
            self.invocation = [invocation]
        self.union_table = union_table
        self.filter = filter

testcases = {
}

def initTestcase(db,  version="v3"):
    testcases.clear()
    folder="print_tokens"
    debuggee = folder+"/versions/"+version+"/"+folder
    read = open("trainset")
    
    fout = popen2.Popen3("gcc -g -o "+folder+"/versions/"+version+"/"+folder+" "+folder+"/versions/"+version+"/"+folder+".c")
    fout2 = popen2.Popen3("gcc -g -o "+folder+"/"+"source"+"/"+folder+" "+folder+"/"+"source"+"/"+folder+".c")
    t = "1"
    result = ""
    while t:
        t = fout.fromchild.readline()
        result = result+t
    t = "1"
    result = ""
    while t:
        t = fout2.fromchild.readline()
        result = result+t 
    
    line=1
    linenumber = 0
    same=1
    #num of testcase
    cnt=5
    while line and linenumber<cnt:
        linenumber += 1
        line=read.readline()
        s = line[:len(line)-1]
        testcases["tcas" + '%d'%linenumber] = Testcase(debuggee, "run "+s)
        #print((folder+"/"+version+"/./"+folder+" "+s))
        fout = popen2.Popen3(folder+"/versions/"+version+"/./"+folder+" "+s)
        fout2=  popen2.Popen3(folder+"/source/./"+folder+" "+s)
        
        t = "1"
        result = ""
        while t:
            t = fout.fromchild.readline()
            result = result+t
        t = "1"
        result2 = ""
        while t:
            t = fout2.fromchild.readline()
            result2 = result2+t
        same = result == result2;
       # print(result)
       # print(result2)
        db.insertTestcase("tcas" + '%d'%linenumber, s,  result,  result2,  same,  debuggee)
    read.close



def saveTC(version="v1"):
    print version
    db = DB3("abc/db/" + version)
    initTestcase(db,  version)

    logtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    log = open("abc/log/" + logtime + ".log", 'w')
    log.write(logtime)
    
    testcase = testcases.values()[0]
    gdb = StateGDB(testcase.debuggee)
    
    read = open(testcase.debuggee+".c")
    line=read.readline()
    linenumber=1
    while line:
        if 0<line.find("return") or 0<line.find("exit("):
            output = gdb.question("b " + '%d'%linenumber)
        line=read.readline()
        linenumber+=1
    read.close

    output = gdb.question("info b")
    db.insertBreakpoint(output)
    
    count=0

    for testcase_name in testcases:
        testcase = testcases.get(testcase_name)

        count+=1
        #print count
        #print "\nStarting GDB on " + testcase.debuggee + testcase.invocation[0]
        log.write("\nStarting GDB on " + testcase.debuggee + testcase.invocation[0])
        
        sys.setrecursionlimit(100)
        
        output = gdb.question(testcase.invocation)
        #fp = open(name, 'a')
        if 1:
        #try:
            while 0>output.find("Program exited normally.") and 0>output.find("Program exited"):

                state = gdb.state()
                
              

                s = output
                s2 = s[s.find("Breakpoint ")+11:s.find(",")]
                db.insertVarValue( testcase_name ,  s2,  state)
                output = gdb.question("c")
#        
    logtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    log.write(logtime)
    log.close()
  

if __name__ == '__main__':
   #global variable,get a list of versions
   a=versionsDebug()
   versions=a.getVersions()
   for v in versions:
     saveTC(v.strip())
  
