import sys,os
import string

class versionsDebug:
    def __init__(self,filename=None,versions=None):
           self.filename="testVersions.txt"
    def getVersions(self):
           fin=open(self.filename,'r')
           self.versions=fin.readlines()
           fin.close()
           return self.versions

  
