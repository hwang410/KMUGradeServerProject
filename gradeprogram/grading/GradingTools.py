import sys
import string
from FileTools import FileTools
from subprocess import call

class GradingTools(object):
    def __init__(self, parameter):
        self.gradeMethod = parameter.gradeMethod 
        self.caseCount = parameter.caseCount
        self.usingLang = parameter.usingLang
        self.version = parameter.version
        self.answerPath = parameter.answerPath
        self.problemName = parameter.problemName
        self.filePath = parameter.filePath
        
    def Grade(self):
        if self.gradeMethod == 'SOLUTION':   # solution
            if self.caseCount > 1:
                result, score = self.SolutionMulti()
                
            else:
                result, score = self.SolutionSingle()
            
        else:   # checker
            if self.caseCount > 1:
                result, score = self.CheckerMulti()
                
            else:
                result, score = self.CheckerSingle()
            
        return result, score
    
    def MakeMulticaseCommand(self):
        # make execution command
        if self.usingLang == 'PYTHON':
            if self.version == '2.7':
                return "%s%s%s" % ('python ', self.runFileName, '.py 1>output.txt 2>core.1')
            elif self.version == '3.4':
                return "%s%s%s" % ('python3 ', self.runFileName, '.py 1>output.txt 2>core.1')
        
        elif self.usingLang == 'C' or self.usingLang == 'C++':
            return './main 1>output.txt'
        
        elif self.usingLang == 'JAVA':
            return "%s%s%s" % ('java ', self.runFileName, ' 1>output.txt 2>core.1')
        
    def SolutionSingle(self):
        # user output file each line compare with answer file each line.
        answerOpenCommand = "%s%s%s" % (self.answerPath, self.problemName, '_cases_total_outputs.txt')
        
        stdLines = FileTools.ReadFileLines('output.txt')
        answerLines = FileTools.ReadFileLines(answerOpenCommand)
        
        count = len(stdLines) - len(answerLines)
        
        _min = len(stdLines) if count < 0 else len(answerLines)
        count = abs(count)
        
        strip = string.rstrip
        
        for i in range(_min):
            stdLine = strip(stdLines[i], '\r\n')
            answerLine = strip(answerLines[i], '\r\n')
            
            if stdLine != answerLine:   # if not same each line
                count += 1
        
        result = 'Solved'
        score = 100
        
        if count > 0:
            result = 'WrongAnswer'
            score = int( ((len(answerLines) - count) * 100) / len(answerLines) )
            
        if score < 0:
            return 'WrongAnswer', 0
            
        return result, score
        
    def CheckerSingle(self):
        copyCommand = "%s%s%s" % (self.answerPath, self.problemName, '.out')
        FileTools.CopyFile(copyCommand,'checker.out')
        
        call('./checker.out 1>result.txt', shell = True)
        
        score = self.GetScore('result.txt')
        
        if score ==100:
            return 'Solved', score
        else:
            return 'WrongAnswer', score
    
    def SolutionMulti(self):
        count = 0
        
        _list = []
        append = _list.append
        
        command = self.MakeMulticaseCommand()
        
        for i in range(1, self.caseCount+1):
            copyCommand = "%s%s%s%i%s" % (self.answerPath, self.problemName,
                                          '_case', i, '_input.txt')
            answerOpenCommand = "%s%s%s%i%s" % (self.answerPath,
                                                self.problemName,
                                                '_case', i, '_output.txt')

            FileTools.CopyFile(copyCommand, 'input.txt')
            
            call(command, shell = True)
            
            answer = FileTools.ReadFileAll(answerOpenCommand)
            student = FileTools.ReadFileAll('output.txt')
            
            if answer != student:
                count += 1
                append(str(i) + ' ')
           
        if count == 0:
            return 'Solved', 100
        
        else:
            self.MakeCaseList(_list)
            return 'WrongAnswer', int( ((self.caseCount - count) * 100) / self.caseCount )
        
    def CheckerMulti(self):
        count = 0
        
        _list = []
        append = _list.append
        
        command = self.MakeMulticaseCommand()
        
        copyCommand = "%s%s%s" % (self.answerPath, self.problemName, '.out')
        
        FileTools.CopyFile(copyCommand, 'checker.out')
        
        for i in range(1, self.caseCount+1):
            copyCommand = "%s%s%s%i%s" % (self.answerPath, self.problemName,
                                          '_case', i, '_input.txt input.txt')
            FileTools.CopyFile(copyCommand, 'input.txt')
            
            call(command, shell = True)
            
            call('./checker.out 1>result.txt', shell = True)
            
            if self.GetScore('result.txt') != 100:
                count += 1
                append(str(i) + ' ')
           
        if count == 0:
            return 'Solved', 100
        
        else:
            self.MakeCaseList(_list)
            return 'WrongAnswer', int( ((self.caseCount - count) * 100) / self.caseCount )
        
    def MakeCaseList(self, _list):
        wf = open('caselist.txt', 'w')
            
        wf.writelines(_list)
                
        wf.close()
            
    def GetScore(self, fileName):
        scores = FileTools.ReadFileLines('result.txt')
        
        return int(scores[0])