import os
import glob
import string
import logging
from gradingResource.listResources import ListResources

class ParameterSetting(object):
    def __init__(self, args):
        self.filePath = args[1]
        self.problemPath = args[2]
        self.saveDirectoryName = args[3]
        self.gradeMethod = args[4]
        self.caseCount = int(args[5])
        self.limitTime = int(args[6])
        self.limitMemory = int(args[7])
        self.usingLang = args[8]
        self.version = args[9]
        self.problemName = args[10]
        
        self.answerPath = "%s%s%s%s%s%s" % (self.problemPath, '/',
                                            self.problemName, '_',
                                            self.gradeMethod, '/')
        
        # make execution file name
        self.filePath = "%s%s" % (self.filePath, '/')
        self.runFileName = self.MakeRunFileName()
        
        os.chdir(self.saveDirectoryName)
        
        logging.debug(self.saveDirectoryName + ' parameter setting')
        
    def MakeRunFileName(self):
        if self.usingLang == ListResources.const.Lang_C or self.usingLang == ListResources.const.Lang_CPP:
            return 'main'
        
        if self.usingLang == ListResources.const.Lang_JAVA:
            fileExtention = '*.java'
            
        else:
            fileExtention = '*.py'
            
        fileList = glob.glob(self.filePath + fileExtention)
        
        if len(fileList) > 1:
            return 'main'
        
        split = string.split
        name = split(fileList[0], '/')
        return split(name[-1], '.')[0]