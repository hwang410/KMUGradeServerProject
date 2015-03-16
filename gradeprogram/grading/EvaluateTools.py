import os
import glob
import math
import runThread

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
                os.system('cp ' + self.answerPath + self.problemName + '_total.in input.txt')
        except Exception as e:
            print e
            return 'error', 0
        
        # make execution command
        command = self.MakeCommand()
        
        runTh = runThread.runThread(command, self.runFileName)
        
        runTh.start()   # thread run -> program run
        
        runTh.join(float(self.limitTime) * 0.0015)
        
        if runTh.isAlive() == True: # if thread is alive
            runTh.shutdown()
            os.system('kill -9 ' + str(runTh.pid))
        
        tsize = os.path.getsize('time.txt')
        
        if tsize > 0:   # if program is terminated normally -> get user time
            fp = open('time.txt', 'r')
            lines = fp.readlines()
            fp.close()
            
            for line in lines:
                if line.find('user') != -1:
                    words = line.split()
                    runTime = int( math.ceil(float(words[1][0] * 60) + float(words[1][2:-1]) * 1000) )
                    
        else:       # if program is abnormally terminated.
            return 'time over', int(self.limitTime * 1.5)
        
        coreSize = 0
        coreList = glob.glob('core.[0-9]*')
        
        if len(coreList) > 0:
            os.path.getsize(coreList[0])
        
        if coreSize == 0:  # if not exist core file -> evaluate output
            if self.gradeMethod == 'Solution':   # solution
                success = self.Solution()
            else:   # checker
                success = self.Checker()
            return success, runTime
        
        elif runTime > self.limitTime:    # time over
            return 'time over', runTime
        
        elif coreSize > 0: # runtime error.
            return 'runtime', runTime
        
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
            return 'ulimit -c unlimited; time (./main 1>output.txt 2>err.err) 2>time.txt'
        
        elif self.usingLang == 'JAVA':
            return 'time (java ' + self.runFileName + ' 1>output.txt 2>core.1) 2>time.txt'
        
    def Solution(self):
        # user output file each line compare with answer file each line.
        try:
            answerFile = open(self.answerPath + self.problemName + '_total.out', 'r')
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
            stdLine = stdLines[i].replace('\r\n', '\n')
            answerLine = answerLines[i].replace('\r\n', '\n')
            
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
            os.system('cp ' + self.answerPath + self.problemName + '.out checker.out')
        except Exception as e:
            print e
            return 'error'
        
        os.system('./checker.out 1>result.txt')
        
        rf = open('reuslt.txt', 'r')
        
        score = rf.readline()
        
        rf.close()
        
        return int(score)