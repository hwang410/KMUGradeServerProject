import os
import sys
from shutil import copyfile

class FileTools(object):
    @staticmethod
    def ReadFileLines(fileName):
        try:
            readFile = open(fileName, 'r')
        except Exception as e:
            print e
            print 'ServerError', 0, 0, 0
            sys.exit()
        
        lines = readFile.readlines()
        readFile.close()
        
        return lines
    
    @staticmethod
    def ReadFileAll(fileName):
        try:
            readFile = open(fileName, 'r') # answer output open
        except Exception as e:
            print e
            print 'ServerError', 0, 0, 0
            sys.exit()
        
        allFile = readFile.read()
        
        readFile.close()
        
        allFile.replace('\r\n', '\n')
        
        return allFile
    
    @staticmethod
    def CopyFile(oldName, newName):
        try:
            if os.path.exists(newName):
                os.remove(newName)
            
            copyfile(oldName, newName)
        except Exception as e:
            print e
            print 'ServerError', 0, 0, 0
            sys.exit()