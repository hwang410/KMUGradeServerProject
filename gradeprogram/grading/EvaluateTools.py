import os
import glob
import math
import time
import runThread
import ptrace
import resource
from subprocess import call

LIMIT_TIME_MULTIPLE = 0.0011
RUN_COMMAND_LIST =[]

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
        
#         pid = os.fork()
#         
#         if pid == 0:
#             self.RunProgram()
#         else:
#             result, res = self.WatchRunProgram(pid)
        
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
            coreSize = os.path.getsize(coreList[0])
        
        if runTime > 100:    # time over -> need modify
            return 'time over', runTime
        
        elif coreSize == 0:  # if not exist core file -> evaluate output
            if self.gradeMethod == 'Solution':   # solution
                success = self.Solution()
            else:   # checker
                success = self.Checker()
            return success, runTime
        
        elif coreSize > 0: # runtime error.
            return 'runtime', 0
        
        else:   # server error
            return 'error', 0
        
    def MakeCommand(self):
        # make execution command
        if self.usingLang == 'PYTHON':
            if self.version == '2.7':
                RUN_COMMAND_LIST.append('/usr/bin/python')
                RUN_COMMAND_LIST.append('/usr/bin/python')
                RUN_COMMAND_LIST.append(self.runFileName + '.py')
                RUN_COMMAND_LIST.append('1>output.txt')
                RUN_COMMAND_LIST.append('2>core.1')
                return 'time (python ' + self.runFileName + '.py 1>output.txt 2>core.1) 2>time.txt'
            elif self.version == '3.4':
                RUN_COMMAND_LIST.append('/usr/local/bin/python3')
                RUN_COMMAND_LIST.append('/usr/local/bin/python3')
                RUN_COMMAND_LIST.append(self.runFileName + '.py')
                RUN_COMMAND_LIST.append('1>output.txt')
                RUN_COMMAND_LIST.append('2>core.1')
                return 'time (python3 ' + self.runFileName + '.py 1>output.txt 2>core.1) 2>time.txt'
        
        elif self.usingLang == 'C' or self.usingLang == 'C++':
            RUN_COMMAND_LIST.append('./main')
            RUN_COMMAND_LIST.append('./main')
            RUN_COMMAND_LIST.append('1>output.txt')
            return 'ulimit -c unlimited; time (./main 1>output.txt) 2>time.txt'
        
        elif self.usingLang == 'JAVA':
            RUN_COMMAND_LIST.append('/usr/bin/java')
            RUN_COMMAND_LIST.append('/usr/in/java')
            RUN_COMMAND_LIST.append(self.runFileName)
            RUN_COMMAND_LIST.append('1>output.txt')
            RUN_COMMAND_LIST.append('2>core.1')
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
    
    def RunProgram(self):
        rlimTime = int(self.limitTime / 1000) + 1
        corefileSize = 1 << 200
        os.nice(19)
        resource.setrlimit(resource.RLIMIT_CORE, (corefileSize,corefileSize))
        resource.setrlimit(resource.RLIMIT_CPU, (rlimTime,rlimTime))
        resource.setrlimit(resource.RLIMIT_AS, (2,1)) #dfasdf
        ptrace.traceme()
        
        if self.usingLang == 'PYTHON' or self.usingLang == 'JAVA':
            os.execl(RUN_COMMAND_LIST[0], RUN_COMMAND_LIST[1], RUN_COMMAND_LIST[2], RUN_COMMAND_LIST[3], RUN_COMMAND_LIST[4])
        elif self.usingLang == 'C' or self.usingLang =='C++':
            os.execl(RUN_COMMAND_LIST[0], RUN_COMMAND_LIST[1], RUN_COMMAND_LIST[2])
            
    def WatchRunProgram(self, pid):
        usingMem = 0
        
        while True:
            wpid, status, res = os.wait4(pid,0)
    
            if os.WIFEXITED(status):
                return 'ok', res
                
            elif os.WIFSIGNALED(status):
                return 'time over', res
            else:
                procFile = open('/proc/' + str(pid) + '/status', 'r')
                fileLines = procFile.readlines()
                
                for i in range(10,20):
                    index = fileLines[i].find()
                    if index != -1:
                        words = fileLines[i].split()
                        temp = int(words[index])
                
                if temp > usingMem:
                    usingMem = temp
                
                ptrace.syscall(pid, 0)
