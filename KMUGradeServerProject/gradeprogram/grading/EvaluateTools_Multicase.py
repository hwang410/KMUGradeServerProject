import os
from EvaluateTools import EvaluateTools

class EvaluateTools_multicase(EvaluateTools):
    def __init__(self, stdNum, usingLang, limitTime, answerRoute, version, gradeMethod, caseCount, runFileName, problemName):
        EvaluateTools.__init__(self, stdNum, usingLang, limitTime, answerRoute, version, gradeMethod, runFileName, problemName)
        self.caseCount = caseCount
        
    def Solution(self):
        count = 0
        _list = ()
        command = self.MakeCommand()
        
        for i in range(1, self.caseCount+1):
            # input.txt file copy
            try:
                os.remove('input.txt') # ...ing....
                os.rename(self.answerRoute + self.problemName + '_case' + i + '.in input.txt') # ...ing...
            except Exception as e:
                print e
                i -= 1
                continue
                
         
            # program run
            os.system(command)
            
            answerFile = open(self.answerRoute + self.problemName + '_case' + str(i) + '.out', 'r') # answer output open
            stdOutput = open('output.txt', 'r') # student output open
            
            answer = answerFile.read()
            student = stdOutput.read()
            
            if answer != student:
                count += 1
                _list.append(i)
                
            answerFile.close()
            stdOutput.close()
           
        if count == 0:
            return 100
        else:
            return int( ((self.caseCount - count) * 100) / self.caseCount )
        
    def Checker(self):
        count = 0
        _list = ()
        command = self.MakeCommand()
        os.system('cp ' + self.answerRoute + self.problemName + '.out checker.out')
        
        for i in range(1, self.caseCount+1):
            # input.txt file copy
            try:
                os.remove('input.txt') # ...ing....
                os.rename(self.answerRoute + self.problemName + '_case' + str(i) + '.in input.txt') # ...ing...
            except Exception as e:
                print e
                i -= 1
                continue
                
         
            # program run
            os.system(command)
            
            os.system('./checker.out 1>result.txt')
            rf = open('reuslt.txt', 'r')
            
            score = rf.readline()
            
            if int(score) != 100:
                count += 1
                _list.append(i)
           
        if count == 0:
            return 100
        else:
            return int( ((self.caseCount - count) * 100) / self.caseCount )