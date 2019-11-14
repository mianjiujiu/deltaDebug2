
import sqlite3
import string
import time


class DB:
    def __init__(self, name):
        logtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print name + logtime + ".db"
        self.conn = sqlite3.connect(name + logtime + ".db")
        self.conn.isolation_level = None
        self.execute("create table if not exists breakpoint(id integer primary key, method TEXT, file TEXT, lineNumber integer)")
        self.execute("create table if not exists testcase(name TEXT primary key, para TEXT, result TEXT, expected TEXT, pass BOOLEAN, debuggee TEXT)")
        self.execute("create table if not exists bp_tc(id integer primary key autoincrement, bp_id integer REFERENCES breakpoint(id), tc_name TEXT REFERENCES testcase(name))")
        self.execute("create table if not exists var(bp_tc_id integer REFERENCES bp_tc(id), path TEXT, label TEXT, address TEXT, size integer, value TEXT, type TEXT)")
        self.conn.commit()

    def execute(self,  cmd):
        return self.conn.execute(cmd)
        
    def insertBreakpoint(self,  b):
        ss = b.split("\n")
        for s in ss:
            if 0<s.find("breakpoint     keep y"):
                s2 = s.split()
                s3 = s2[8].split(":")
                self.execute("insert into breakpoint values (%s, '%s', '%s', %s)"%(s2[0],  s2[6],  s3[0],  s3[1]))
        self.conn.commit()

    def insertTestcase(self, name, s,  result,  result_right,  same,  debuggee):
        self.execute("insert into testcase values ('%s', '%s', '%s', '%s', %d, '%s')"%(name,   s,  result,   result_right,  same,  debuggee))
        
    def insertVarValue(self, testcase,  breakpoint,  value):
        cur = self.execute("insert into bp_tc(bp_id, tc_name) values (%s, '%s')"%(breakpoint,  testcase))
        cur = self.execute("select last_insert_rowid()"); 
        c = cur.fetchall()[0][0]
        for var in value:
            self.execute("insert into var values (%d, '%s', '%s', '%s', %d, '%s', '%s')"%(c,  var[0],  var[1],  var[2],  var[3],  var[4],  var[5]))
        self.conn.commit()
        
    def closeDB(self):
        self.conn.close()

class DB2:
    def __init__(self, name):
        logtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print name + logtime + ".db"
        self.conn = sqlite3.connect(name + logtime + ".db")
        self.conn.isolation_level = None
        self.execute("create table if not exists breakpoint(id integer primary key, method TEXT, file TEXT, lineNumber integer)")
        self.execute("create table if not exists testcase(name TEXT primary key, para TEXT, result TEXT, expected TEXT, pass BOOLEAN, debuggee TEXT)")
        self.execute("create table if not exists bp_tc(id integer primary key autoincrement, bp_id integer REFERENCES breakpoint(id), tc_name TEXT REFERENCES testcase(name))")
        self.execute("create table if not exists var(bp_tc_id integer REFERENCES bp_tc(id), var TEXT, frame integer, value TEXT)")
        self.conn.commit()

    def execute(self,  cmd):
        return self.conn.execute(cmd)

    def insertBreakpoint(self,  b):
        ss = b.split("\n")
        for s in ss:
            if 0<s.find("breakpoint     keep y"):
                s2 = s.split()
                s3 = s2[8].split(":")
                self.execute("insert into breakpoint values (%s, '%s', '%s', %s)"%(s2[0],  s2[6],  s3[0],  s3[1]))
        self.conn.commit()

    def insertTestcase(self, name, s,  result,  result_right,  same,  debuggee):
        self.execute("insert into testcase values ('%s', '%s', '%s', '%s', %d, '%s')"%(name,   s,  result,   result_right,  same,  debuggee))

    def insertVarValue(self, testcase,  breakpoint,  state):
        cur = self.execute("insert into bp_tc(bp_id, tc_name) values (%s, '%s')"%(breakpoint,  testcase))
        cur = self.execute("select last_insert_rowid()"); 
        c = cur.fetchall()[0][0]
        for var in state:
            self.execute("insert into var values (%d, '%s', %d, '%s')"%(c,  var[0],  var[1],  state[var]))
        self.conn.commit()

    def closeDB(self):
        self.conn.close()

class DB3:
    def __init__(self, name):
        logtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print name + logtime + ".db"
      
        self.conn = sqlite3.connect(name  + ".db")
        self.conn.isolation_level = None
        self.execute("create table if not exists breakpoint(id integer primary key, method TEXT, file TEXT, lineNumber integer)")
        self.execute("create table if not exists testcase(name TEXT primary key, para TEXT, result TEXT, expected TEXT, pass BOOLEAN, debuggee TEXT)")
        self.execute("create table if not exists bp_tc(id integer primary key autoincrement, bp_id integer REFERENCES breakpoint(id), tc_name TEXT REFERENCES testcase(name), val TEXT)")
        self.conn.commit()

    def execute(self,  cmd):
        return self.conn.execute(cmd)

    def insertBreakpoint(self,  b):
        ss = b.split("\n")
        for s in ss:
            if 0<s.find("breakpoint     keep y"):
                s2 = s.split()
                s3 = s2[8].split(":")
                self.execute("insert into breakpoint values (%s, '%s', '%s', %s)"%(s2[0],  s2[6],  s3[0],  s3[1]))
        self.conn.commit()

    def insertTestcase(self, name, s,  result,  result_right,  same,  debuggee):
	ss = str(s).replace("'", "''")
        self.execute("insert into testcase values ('%s', '%s', '%s', '%s', %d, '%s')"%(name,   ss,  result,   result_right,  same,  debuggee))

    def insertVarValue(self, testcase,  breakpoint,  state):
        ss = str(state).replace("'", "''")
        cur = self.execute("insert into bp_tc(bp_id, tc_name, val) values (%s, '%s', '%s')"%(breakpoint,  testcase, ss))

    def closeDB(self):
        self.conn.close()
