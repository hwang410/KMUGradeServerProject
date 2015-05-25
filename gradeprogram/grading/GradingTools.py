import string
from FileTools import FileTools
from subprocess import call
from gradingResource.enumResources import ENUMResources
from gradingResource.listResources import ListResources

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
        if self.gradeMethod == ENUMResources.const.SOLUTION:   # solution
            if self.caseCount > 1:
                result, score = self.GradeSolutionMulti()
                
            else:
                result, score = self.GradeSolutionSingle()
            
        else:   # checker
            if self.caseCount > 1:
                result, score = self.GradeCheckerMulti()
                
            else:
                result, score = self.GradeCheckerSingle()
            
        return result, score
    
    def MakeMulticaseCommand(self):
        # make execution command
        if self.usingLang == ListResources.const.Lang_PYTHON:
            if self.version == ListResources.const.PYTHON_VERSION_TWO:
                return "%s%s%s" % ('python ', self.runFileName, '.py 1>output.txt 2>core.1')
            elif self.version == ListResources.const.PYTHON_VERSION_THREE:
                return "%s%s%s" % ('python3 ', self.runFileName, '.py 1>output.txt 2>core.1')
        
        elif self.usingLang == ListResources.const.Lang_C or self.usingLang == ListResources.const.Lang_CPP:
            return './main 1>output.txt'
        
        elif self.usingLang == ListResources.const.Lang_JAVA:
            return "%s%s%s" % ('java ', self.runFileName, ' 1>output.txt 2>core.1')
        
    def GradeSolutionSingle(self):
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
        
        result = ENUMResources.const.SOLVED
        score = 100
        
        if count > 0:
            result = ENUMResources.const.WRONG_ANSWER
            score = int( ((len(answerLines) - count) * 100) / len(answerLines) )
            
        if score < 0:
            return ENUMResources.const.WRONG_ANSWER, 0
            
        return result, score
        
    def GradeCheckerSingle(self):
        copyCommand = "%s%s%s" % (self.answerPath, self.problemName, '.out')
        FileTools.CopyFile(copyCommand,'checker.out')
        
        call('./checker.out 1>result.txt', shell = True)
        
        score = self.GetScore('result.txt')
        
        if score ==100:
            return ENUMResources.const.SOLVED, score
        else:
            return ENUMResources.const.WRONG_ANSWER, score
    
    def GradeSolutionMulti(self):
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
            return ENUMResources.const.SOLVED, 100
        
        else:
            self.MakeCaseList(_list)
            return ENUMResources.const.WRONG_ANSWER, int( ((self.caseCount - count) * 100) / self.caseCount )
        
    def GradeCheckerMulti(self):
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
            return ENUMResources.const.SOLVED, 100
        
        else:
            self.MakeCaseList(_list)
            return ENUMResources.const.WRONG_ANSWER, int( ((self.caseCount - count) * 100) / self.caseCount )
        
    def MakeCaseList(self, _list):
        wf = open('caselist.txt', 'w')
            
        wf.writelines(_list)
                
        wf.close()
            
    def GetScore(self, fileName):
        scores = FileTools.ReadFileLines('result.txt')
        
        return int(scores[0])