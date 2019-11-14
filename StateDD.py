
import sys, os
import string
import re
import time
import popen2
import sqlite3
import cStringIO

# Own modules
import check
from StateGDB import StateGDB
from TimedMessage import TimedMessage
from DD import DD
from DB import DB3
from rank import rank

folder="print_tokens"
RightVersion="./"+folder+"/source/"+folder

class StateDD(DD):
    debug_state = 1

    def __init__(self, debuggee, args_1, args_2,  version):
        DD.__init__(self)
        self.debugcase1 = args_1
        self.debugcase2 = args_2
        self.gdb = StateGDB(debuggee)
        self.gdb2 = StateGDB(debuggee)

        self.conn = sqlite3.connect("abc/"+version+".db")
        print "abc/"+version+".db"
        self.count_all = self.conn.execute("select count(*) from testcase").fetchall()[0][0]
        self.count_fail = self.conn.execute("select count(*) from testcase where pass=0").fetchall()[0][0]
        cur = self.conn.execute("select para, pass from testcase where name='%s'"%args_1).fetchall()
        assert cur[0][1] == 1
        self.args_1 = cur[0][0]
        self.gdb2.question("set args " + self.args_1)
            
        cur = self.conn.execute("select para, pass from testcase where name='%s'"%args_2).fetchall()
        assert cur[0][1] == 0
        self.args_2 = cur[0][0]

        cur = self.conn.execute("select lineNumber from breakpoint").fetchall()
        
        self.syncpoints = []
        for cur2 in cur:
            self.syncpoints.append(cur2[0])
            self.gdb.break_at(cur2[0])
            self.gdb2.break_at(cur2[0])
        print self.syncpoints
        
        self.check = check.CheckResult(RightVersion,  self.syncpoints)
        
#        print self.args_1
#        print self.args_2
        

    def set_syncpoint(self):
        
        self.gdb.disableAll()
        self.gdb.enable([self.syncpoint])
        
        self.gdb.question("set args " + self.args_1)
        self.gdb.question("run")
        self.state_1 = self.gdb.state()
        #if self.debug_state:
            #print "state_1 =", self.state_1

        
        self.gdb.question("set args " + self.args_2)
        self.gdb.question("run")
        self.state_2 = self.gdb.state()
        #if self.debug_state:
           #print "state_2 =", self.state_2
        

        self.deltas = self.gdb.deltas(self.state_1, self.state_2)

        if self.debug_state:
            serial = 1
            for delta in self.deltas:
                (var, value_1, value_2) = delta
                (name, frame) = var
                #print "Delta #" + `serial` + " at frame " + `frame` + ":"
                #print `name` + " = " + value_1 + " / " + value_2
                serial = serial + 1

        self.gdb.disable([self.syncpoint])

    def all_deltas(self):
        return self.deltas

    def _test2(self,  c):
        print c
        self.gdb.disableAll()
        self.gdb.enable([self.syncpoint])
        self.gdb.question("set args " + self.args_1)
        output=self.gdb.question("run")
        self.gdb.apply_deltas(c)
        self.gdb.disableAll()
        output=self.gdb.question("cont")
        print output
        if string.find(output, "1") >= 0:
            print "DD.FAIL"
            return DD.FAIL
        if string.find(output, "0") >= 0:
            print "DD.PASS"
            return DD.PASS
        print "DD.UNRESOLVED"
        return DD.UNRESOLVED
        
    def _test(self, c):
        
        self.gdb.disableAll()
        self.gdb.enable([self.syncpoint])
        self.gdb.question("set args " + self.args_1)
        output=self.gdb.question("run")
        self.gdb.apply_deltas(c)
        self.gdb.enableAll()

        #print self.syncpoint
        print c

        fail = {"max":0}
        pas = {"max":0}
        sum = {"max":0}
        total = 0
        top = rank(20)
        while 0>output.find("Program exited normally.") and 0>output.find("Program exited"):

            state = self.gdb.state()
            """s=output
            output = self.gdb.question("c")
            if 0>output.find("Program exited normally.") and 0>output.find("Program exited"):
                state = self.gdb.state()
            else:
                output = s"""
            
            s = output
            s2 = s[s.find("Breakpoint ")+11:s.find(",")]
            cur = self.conn.execute("select val,tc_name,pass  from bp_tc join breakpoint on bp_tc.bp_id=breakpoint.id join testcase on bp_tc.tc_name=testcase.name where breakpoint.id=%s"%s2).fetchall()
            total= len(state)
            
            #print state
            #print cur[0][0]
            
            for ccur in cur:
               if ccur[1]!=self.debugcase1 and ccur[1]!=self.debugcase2:
                    s = eval(ccur[0])
                    join = self.joins(state,  s)
                    top.insert(ccur[2],  len(join))
                    self.saveToDic(sum,  len(join))
                    if ccur[2] == 0:
                        self.saveToDic(fail,  len(join))
                    else:
                        self.saveToDic(pas,  len(join))
            self.gdb.disableAll()
            output = self.gdb.question("c")
            break
        
        """print total
        print "fail"
        print fail
        print 'pas'
        print pas
        print 'sum'
        print sum
        print 'top'
        print top.collection()
        print top.collection_t()"""

        (f,  p) = self.getMax(fail,  pas,  total)
        print "f:%d,p:%d,c_f:%d,c_a:%d"%(f, p,  self.count_fail, self.count_all)
        if f+p==0:
            return DD.UNRESOLVED
        print 1.0*f/(f+p)/3, 1.0*(self.count_fail-1)/self.count_all
        print "      -------------------------                "
        if 1.0*f/(f+p)/3>1.0*(self.count_fail-1)/self.count_all:
            print "DD.FAIL"
            print 
            result = DD.FAIL
        else :
            print "DD.PASS"
            print 
            result = DD.PASS
        newState=self.gdb.state()
        self.check.check(self.args_1,  newState,  output,  [self.syncpoint],  result==DD.PASS)

        print "      -------------------------                "
        return result
        print "DD.UNRESOLVED"
        print 
        return DD.UNRESOLVED

    def getMax(self,  fail,  pas,  total):
        
        f = 0
        p=0
        for x in range((total+1)*4/10, total):
            if fail.has_key(x):
                f+=fail[x]
            if pas.has_key(x):
                p+=pas[x]
        return (f,  p)

    def saveToDic(self,  dic,  val):
        if dic.has_key(val):
            dic[val]+=1
        else:
            dic[val] = 1
        
        if dic["max"]<val:
            dic["max"] = val

    #def compare(self,  cur,  state):

    # Return (opaque) list of joins
    def joins(self, state_1, state_2):
        join = []
        for var in state_1.keys():
            #if var[0]=="argc" or var[0].find("argv[")==0:
            #    continue
            value_1 = state_1[var]
            if not state_2.has_key(var):
                continue                # Uncomparable
            value_1 = state_1[var]
            value_2 = state_2[var]
            if value_1 == value_2:
                join.append((var, value_1, value_2))
        return join


    def bitstring(self, n, bits):
        s = ""
        for i in range(bits):
            if n & (1 << i):
                s += "+"
            else:
                s += "-"
        return s


    def cause_effect_chain(self):
        t1 = TimedMessage("Computing cause-effect chain")
        causes = []
        
        #for i in range(len(self.syncpoints)):
        
        output=self.gdb2.question("run")
        while 0>output.find("Program exited normally.") and 0>output.find("Program exited"):
            s = output
            i = eval(s[s.find("Breakpoint ")+11:s.find(",")])-1
            syncpoint = self.syncpoints[i]
            print
            print "At",self.debugcase1,  self.debugcase2,   `syncpoint`
            print "---" + "-" * len(`syncpoint`)
            print
            
            self.syncpoint=i+1
            self.set_syncpoint()
            
            (c, c1, c2) = self.dd(self.all_deltas())
            print 
            print "c:"
            print c
            print "c1:"
            print c1
            print "c2:"
            print c2
            causes.append((syncpoint,  c))

            #print [self.syncpoint]
            self.gdb2.disable([self.syncpoint])
            output = self.gdb2.question("c")
        t1.outcome = "done"
        
        print "++++cause_effect_chain"
        return causes
    
    def print_cause_effect_chain(self):
        causes = self.cause_effect_chain()

        s = cStringIO.StringIO()
        saved_stdout = sys.stdout
        sys.stdout = s

        print "Cause-effect chain for " + `self.gdb.debuggee`
        print "=======================" + "=" * len(`self.gdb.debuggee`)
        print

        print "Arguments are " + self.args_2,
        print "(instead of " + self.args_1 + ")"
        
        
        for a in causes:
            print "therefore at " + `a[0]` + ",",

            for delta in a[1]:
                (var, value_1, value_2) = delta
                (name, frame) = var
                print name, "=", value_2, "(instead of", value_1 + ")"

        print "therefore the run fails."
        
        sys.stdout = saved_stdout
        return s.getvalue()

