
import sys, os
import string
import re
import time
import popen2
import sqlite3
import cStringIO

# Own modules
from StateGDB import StateGDB

class CheckResult:
    def __init__(self,  debuggee,  breakPoints):
        self.count = {"right":0,  "total":0,  "result different":0}
        self.gdb = StateGDB(debuggee)
        for b in breakPoints:
            self.gdb.break_at(b)
        
    def check(self,  args,  c,  output,  breakpoint,  right):
        self.gdb.disableAll()
        self.gdb.enable(breakpoint)
        self.gdb.question("info b")
        self.gdb.question("set args " + args)
        self.gdb.question("run")

        

        self.gdb.apply_deltas(c)
        
       
        self.gdb.disableAll()
        output_right = self.gdb.question("c")
        
        print "output---"+output
        print "output_right---"+output_right
        
        self.count["total"]+=1
        if(right):
          if(output != output_right):
            self.count["result different"]+=1
          else:
            self.count["right"]+=1
        else:   
          if (output != output_right):
            self.count["right"]+=1
          else:
            self.count["result different"]+=1
        
        return output == output_right
    
    def __del__(self):
        print 
        print "result count:"
        print self.count
        print

