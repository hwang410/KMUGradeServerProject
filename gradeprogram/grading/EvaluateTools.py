import os
import glob
import time
import ptrace
import resource
from subprocess import call

RUN_COMMAND_LIST = []

class EvaluateTools():
    def __init__(self, usingLang, limitTime, limitMemory, answerPath, version, gradeMethod, runFileName, problemName, caseCount):
        self.usingLang = usingLang
        self.limitTime = limitTime
        self.limitMemory = limitMemory
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
                call('cp ' + self.answerPath + self.problemName + '_cases_total_inputs.in input.txt', shell = True)
        except Exception as e:
            print e
            return 'error', 0
        
        # make execution command
        self.MakeCommand()
                
        pid = os.fork()
         
        if pid == 0:
            self.RunProgram()
        else:
            result, time, usingMem = self.WatchRunProgram(pid)
        print time
        userTime = int(time * 1000)
        
        if result == 'time over':
            return 'time over', userTime, usingMem
        
        elif result == 'runtime':
            return 'runtime', 0, 0

        if userTime > self.limitTime:
            return 'time over', userTime, usingMem
        
        coreSize = 0
        coreList = glob.glob('core.[0-9]*')
        
        if len(coreList) > 0:
            coreSize = os.path.getsize(coreList[0])
        
        if coreSize == 0:  # if not exist core file -> evaluate output
            if self.gradeMethod == 'Solution':   # solution
                success = self.Solution()
            else:   # checker
                success = self.Checker()
            return success, userTime, usingMem
        
        elif coreSize > 0: # runtime error.
            return 'runtime', 0, 0
        
        else:   # server error
            return 'error', 0, 0
        
    def MakeCommand(self):
        # make execution command
        if self.usingLang == 'PYTHON':
            if self.version == '2.7':
                RUN_COMMAND_LIST.append('/usr/bin/python')
                RUN_COMMAND_LIST.append('/usr/bin/python')
                RUN_COMMAND_LIST.append(self.runFileName + '.py')
                
            elif self.version == '3.4':
                RUN_COMMAND_LIST.append('/usr/local/bin/python3')
                RUN_COMMAND_LIST.append('/usr/local/bin/python3')
                RUN_COMMAND_LIST.append(self.runFileName + '.py')
                
        elif self.usingLang == 'C' or self.usingLang == 'C++':
            RUN_COMMAND_LIST.append('./main')
            RUN_COMMAND_LIST.append('./main')
            
        elif self.usingLang == 'JAVA':
            RUN_COMMAND_LIST.append('/usr/bin/java')
            RUN_COMMAND_LIST.append('/usr/bin/java')
            RUN_COMMAND_LIST.append(self.runFileName)
        
    def Solution(self):
        # user output file each line compare with answer file each line.
        try:
            answerFile = open(self.answerPath + self.problemName + '_cases_total_outputs.out', 'r')
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
        os.nice(19)
        
        fd1 = os.open('output.txt', os.O_RDWR|os.O_CREAT)
        os.dup2(fd1,1)
        if self.usingLang == 'JAVA' or self.usingLang == 'PYTHON':
            fd2 = os.open('core.1', os.O_RDWR|os.O_CREAT)
            os.dup2(fd2,2)
        
        rlimTime = int(self.limitTime / 1000) + 1
        corefileSize = 1 << 20
        resource.setrlimit(resource.RLIMIT_CORE, (corefileSize,corefileSize))
        resource.setrlimit(resource.RLIMIT_CPU, (rlimTime,rlimTime))
        ptrace.traceme()
        
        if self.usingLang == 'PYTHON' or self.usingLang == 'JAVA':
            os.execl(RUN_COMMAND_LIST[0], RUN_COMMAND_LIST[1], RUN_COMMAND_LIST[2])
        elif self.usingLang == 'C' or self.usingLang =='C++':
            os.execl(RUN_COMMAND_LIST[0], RUN_COMMAND_LIST[1])
            
    def WatchRunProgram(self, pid):
        usingMem = 0
        temp = 0
        
        while True:
            wpid, status, res = os.wait4(pid,0)
    
            if os.WIFEXITED(status):
                return 'ok', res[0], usingMem
            
            exitCode = os.WEXITSTATUS(status)
            if exitCode != 0 and exitCode != 5 and exitCode != 17:
                return 'runtime', 0, 0 
                
            elif os.WIFSIGNALED(status):
                return 'time over', res[0], usingMem
            else:
                procFile = open('/proc/' + str(pid) + '/status', 'r')
                fileLines = procFile.readlines()

                for i in range(15,20):
                    index = fileLines[i].find('VmRSS')
                    if index != -1:
                        words = fileLines[i].split()
                        temp = int(words[index+1])
                
                if temp > usingMem:
                    usingMem = temp
                
                ptrace.syscall(pid, 0)
