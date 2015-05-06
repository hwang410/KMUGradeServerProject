import os
import glob
import sys
import string
import CompileTools
from grading import ExecutionTools
from grading import GradingTools

class InterfaceGrade(object):
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
        
        dirName = "%s%i%i" % (self.stdNum, self.problemNum, self.submitCount)
        os.mkdir(dirName)
        os.chdir(dirName)
        
    def Compile(self):
        _compile = CompileTools.CompileTools(self.filePath, self.stdNum,
                                             self.usingLang, self.version,
                                             self.runFileName)
        success = _compile.CodeCompile()
        
        return success, self.stdNum, self.problemNum, self.courseNum, self.submitCount
        
    def Evaluation(self):
        score = 0
        execution = ExecutionTools.ExecutionTools(self.usingLang, self.limitTime,
                                                 self.limitMemory, self.answerPath,
                                                 self.version, self.runFileName,
                                                 self.problemName, self.caseCount)
            
        success, runTime, usingMem = execution.Execution()
        
        if success == 'Grading':
            evaluation = GradingTools.GradingTools(self.gradeMethod, self.caseCount,
                                                   self.usingLang, self.version,
                                                   self.answerPath, self.problemName,
                                                   self.filePath)
             
            success, score = evaluation.Grade()
            
        print success, score, runTime, usingMem
        sys.exit()
    
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