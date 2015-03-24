import os
import glob
import math
import time
import runThread
from subprocess import call

LIMIT_TIME_MULTIPLE = 0.0011

class EvaluateTools():
    def __init__(self, usingLang, limitTime, answerPath, version, gradeMethod, runFileName, problemName, caseCount):
        self.usingLang = usingLang
        self.limitTime = limitTime
        self.answerPath = answerPath
        self.version = version
        self.gradeMethod = gradeMethod
        self.runFileName = runFileName
        self.problemName = problemName
        self.caseCount = caseCount
        
    def Execution(self):
        # copy input data
        try:
            if self.caseCount == 1:
                call('cp ' + self.answerPath + self.problemName + '_total_inputs.in input.txt', shell = True)
        except Exception as e:
            print e
            return 'error', 0
        
        # make execution command
        command = self.MakeCommand()
        
        runTh = runThread.runThread(command, self.runFileName)
        
        runTh.start()   # thread run -> program run
        
        runTh.join(float(self.limitTime) * LIMIT_TIME_MULTIPLE)
        
        if runTh.isAlive() == True: # if thread is alive
            runTh.shutdown()
            time.sleep(0.07)
        
        tsize = os.path.getsize('time.txt')

        if tsize > 0:   # if program is terminated normally -> get user time
            fp = open('time.txt', 'r')
            lines = fp.readlines()
            fp.close()
            
            for line in lines:
                if line.find('user') != -1:
                    words = line.split()
                    runTime = int( math.ceil(float(words[1][0] * 60) + float(words[1][2:-1]) * 1000) )
                    break;
                    
        else:       # if program is abnormally terminated.
            return 'time over', self.limitTime
        
        coreSize = 0
        coreList = glob.glob('core.[0-9]*')
        
        if len(coreList) > 0:
            os.path.getsize(coreList[0])
        
        if runTime > 0.001:    # time over -> need modify
            return 'time over', runTime
        
        elif coreSize == 0:  # if not exist core file -> evaluate output
            if self.gradeMethod == 'Solution':   # solution
                success = self.Solution()
            else:   # checker
                success = self.Checker()
            return success, runTime
        
        elif coreSize > 0: # runtime error.
            return 'runtime'
        
        else:   # server error
            return 'error', 0
        
    def MakeCommand(self):
        # make execution command
        if self.usingLang == 'PYTHON':
            if self.version == '2.7':
                return 'time (python ' + self.runFileName + '.py 1>output.txt 2>core.1) 2>time.txt'
            elif self.version == '3.4':
                return 'time (python3 ' + self.runFileName + '.py 1>output.txt 2>core.1) 2>time.txt'
        
        elif self.usingLang == 'C' or self.usingLang == 'C++':
            return 'ulimit -c unlimited; time (./main 1>output.txt) 2>time.txt'
        
        elif self.usingLang == 'JAVA':
            return 'time (java ' + self.runFileName + ' 1>output.txt 2>core.1) 2>time.txt'
        
    def Solution(self):
        # user output file each line compare with answer file each line.
        try:
            answerFile = open(self.answerPath + self.problemName + '_total_outputs.out', 'r')
        except Exception as e:
            print e
            return 'error'
        
        stdOutput = open('output.txt', 'r')
        
        stdLines = stdOutput.readlines()
        answerLines = answerFile.readlines()
        
        answerFile.close()
        stdOutput.close()
        
        count = len(stdLines) - len(answerLines)
        
        if count < 0 :
            _min = len(stdLines)
            count = abs(count)
        else:
            _min = len(answerLines)
            count = count
        
        for i in range(_min):
            stdLine = stdLines[i].strip('\r\n')
            answerLine = answerLines[i].strip('\r\n')
            
            if stdLine != answerLine:   # if not same each line
                count += 1
        
        if count == 0:
            return 100
        else:
            score = int( ((len(answerLines) - count) * 100) / len(answerLines) )
            
            if score < 0:
                return 0
            
            return score
        
    def Checker(self):
        try:
            call('cp ' + self.answerPath + self.problemName + '.out checker.out', shell = True)
        except Exception as e:
            print e
            return 'error'
        
        call('./checker.out 1>result.txt', shell = True)
        
        rf = open('reuslt.txt', 'r')
        
        score = rf.readline()
        
        rf.close()
        
        return int(score)