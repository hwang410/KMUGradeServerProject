import os
import sys
from shutil import copyfile
from gradingResource.enumResources import ENUMResources

class FileTools(object):
    @staticmethod
    def ReadFileLines(fileName):
        try:
            readFile = open(fileName, 'r')
        except Exception as e:
            print e
            print ENUMResources.const.SERVER_ERROR, 0, 0, 0
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
            print ENUMResources.const.SERVER_ERROR, 0, 0, 0
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
            print ENUMResources.const.SERVER_ERROR, 0, 0, 0
            sys.exit()