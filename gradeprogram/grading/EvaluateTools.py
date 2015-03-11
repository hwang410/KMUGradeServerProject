import os
import glob
import math
import runThread

class EvaluateTools():
    def __init__(self, stdNum, usingLang, limitTime, answerRoute, version, gradeMethod, runFileName, problemName):
        self.stdNum = stdNum
        self.usingLang = usingLang
        self.limitTime = limitTime
        self.answerRoute = answerRoute
        self.version = version
        self.gradeMethod = gradeMethod
        self.runFileName = runFileName
        self.problemName = problemName
        
    def Execution(self):
        command = self.MakeCommand()
        
        runTh = runThread.runThread(command, self.stdNum)
        
        runTh.start()   # program run
        
        runTh.join(float(self.limitTime) * 0.0015)
        
        if runTh.isAlive() == True: # if thread is running
            runTh.shutdown(self.stdNum)
            os.system('kill -9 ' + str(runTh.pid))
        
        tsize = os.path.getsize('time.txt')
        
        if tsize > 0: # if program is terminated normally.
            fp = open('time.txt', 'r')
            lines = fp.readlines()
            for i in range(len(lines)):
                if lines[i].find('user') != -1:
                    words = lines[i].split()
                    runTime = int( math.ceil( float(words[1][2:-1] ) * 1000) )
                    
        else:       # if program is abnormally terminated.
            return 'time over', int(self.limitTime * 1.5)
        
        coreCount = len(glob.glob('core*'))
        
        if coreCount == 0 or os.path.getsize('core.txt') == 0: # if core file is not created.
            if self.gradeMethod == 0:   # solution
                success = self.Solution()
            else:   # checker
                success = self.Checker()
            return success, runTime
        
        elif runTime > self.limitTime:    # if time over.
            return 'time over', runTime
        
        elif coreCount > 0 and os.path.getsize('core.txt') > 0: # if runtime error.
            return 'runtime', runTime
        else:
            return 'error', 0
        
    def MakeCommand(self):
        if self.usingLang == 0:
            if self.version == '2.7':
                return 'time (python ' + self.runFileName + '.py 1>output.txt 2>core.txt) 2>time.txt'
            elif self.version == '3.4':
                return 'time (python3 ' + self.runFileName + '.py 1>output.txt 2>core.txt) 2>time.txt'
        
        elif self.usingLang == 1 or self.usingLang == 2:
            return 'time (./' + self.stdNum + ' 1>output.txt 2>err.err) 2>time.txt'
        
        elif self.usingLang == 3:
            return 'time (java ' + self.runFileName + ' 1>output.txt 2>core.txt) 2>time.txt'
        
    def Solution(self):
        answerFile = open(self.answerRoute + self.problemName + '_total.out', 'r')
        stdOutput = open('output.txt', 'r')
    
        stdLines = stdOutput.readlines()
    
        answerLines = answerFile.readlines()
        
        count = len(stdLines) - len(answerLines)
        
        if count < 0 :
            _min = len(stdLines)
            count = abs(count)
        else:
            _min = len(answerLines)
            count = count
            
        for i in range(_min):
            if stdLines[i] != answerLines[i]:
                count += 1
                
        if count == 0:
            return 100
        else:
            return int( ((len(answerLines) - count) * 100) / len(answerLines) )
        
    def Checker(self):
        os.system('cp ' + self.answerRoute + self.problemName + '.out checker.out')
        os.system('./checker.out 1>result.txt')
        rf = open('reuslt.txt', 'r')
        score = rf.readline()
        
        return int(score)