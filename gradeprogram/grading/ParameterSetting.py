import os
import glob
import string
import logging

class ParameterSetting(object):
    def __init__(self, args):
        self.filePath = args[1]
        self.problemPath = args[2]
        self.stdNum = args[3]
        self.problemNum = int(args[4])
        self.gradeMethod = args[5]
        self.caseCount = int(args[6])
        self.limitTime = int(args[7])
        self.limitMemory = int(args[8])
        self.usingLang = args[9]
        self.version = args[10]
        self.courseNum = int(args[11])
        self.submitCount = int(args[12])
        self.problemName = args[13]
        
        self.answerPath = "%s%s%s%s%s%s" % (self.problemPath, '/', self.problemName, '_', self.gradeMethod, '/')
        
        # make execution file name
        self.filePath = "%s%s" % (self.filePath, '/')
        self.runFileName = self.MakeRunFileName()
        
        dirName = "%s%i%i%i" % (self.stdNum, self.problemNum, self.courseNum, self.submitCount)
        os.mkdir(dirName)
        os.chdir(dirName)
        
        logging.debug(self.stdNum + ' parameter setting')
        
    def MakeRunFileName(self):
        if self.usingLang == 'C' or self.usingLang == 'C++':
            return 'main'
        
        if self.usingLang == 'JAVA':
            fileExtention = '*.java'
            
        else:
            fileExtention = '*.py'
            
        fileList = glob.glob(self.filePath + fileExtention)
        
        if len(fileList) > 1:
            return 'main'
        
        split = string.split
        name = split(fileList[0], '/')
        return split(name[-1], '.')[0]