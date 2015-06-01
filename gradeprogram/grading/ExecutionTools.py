import os
import sys
import glob
import string
import ptrace
import resource
from shutil import copyfile
from FileTools import FileTools
from GradingCommand import GradingCommand
from gradingResource.enumResources import ENUMResources
from gradingResource.listResources import ListResources

RUN_COMMAND_LIST = []

class ExecutionTools(object):
    def __init__(self, parameter):
        self.usingLang = parameter.usingLang
        self.limitTime = parameter.limitTime
        self.limitMemory = parameter.limitMemory
        self.answerPath = parameter.answerPath
        self.version = parameter.version
        self.runFileName = parameter.runFileName
        self.problemName = parameter.problemName
        self.caseCount = parameter.caseCount
        
    def Execution(self):
        # copy input data
        try:
            if self.caseCount > 0:
                copyCommand = "%s%s%s" % (self.answerPath, self.problemName, '_cases_total_inputs.txt')
                copyfile(copyCommand, 'input.txt')
        except Exception as e:
            print e
            print ENUMResources.const.SERVER_ERROR, 0, 0, 0
            sys.exit()
        
        # make execution command
        runCommandList = GradingCommand.MakeExecuteCommand(self.usingLang, self.runFileName, self.version)
                
        pid = os.fork()
         
        if pid == 0:
            self.RunProgram(runCommandList)
        
        else:
            result, time, usingMem = self.WatchRunProgram(pid)
        
        userTime = int(time * 1000)
        
        coreList = glob.glob('core.[0-9]*')
        
        if len(coreList) > 0 and os.path.getsize(coreList[0]) > 0:
            result = ENUMResources.const.RUNTIME_ERROR
        
        elif userTime > self.limitTime:
            result = ENUMResources.const.TIME_OVER 
        
        if not result:
            self.ResultError(result, userTime, usingMem)
        
        return 'Grading', userTime, usingMem
    
    def RunProgram(self, runCommandList):
        os.nice(19)
        
        reditectionSTDOUT = os.open('output.txt', os.O_RDWR|os.O_CREAT)
        os.dup2(reditectionSTDOUT,1)
        
        rlimTime = int(self.limitTime / 1000) + 1
        
        resource.setrlimit(resource.RLIMIT_CORE, (1024,1024))
        resource.setrlimit(resource.RLIMIT_CPU, (rlimTime,rlimTime))
        
        ptrace.traceme()
        
        if self.usingLang == ListResources.const.Lang_PYTHON or self.usingLang == ListResources.const.Lang_JAVA:
            reditectionSTDERROR = os.open('core.1', os.O_RDWR|os.O_CREAT)
            os.dup2(reditectionSTDERROR,2)
            
            os.execl(runCommandList[0], runCommandList[1], runCommandList[2])
            
        else:
            os.execl(runCommandList[0], runCommandList[1])
            
    def WatchRunProgram(self, pid):
        usingMem = 0
        
        while True:
            wpid, status, res = os.wait4(pid,0)
    
            if os.WIFEXITED(status):
                return True, res[0], usingMem
            
            exitCode = os.WEXITSTATUS(status)
            if exitCode != 5 and exitCode != 0 and exitCode != 17:
                ptrace.kill(pid)
                return ENUMResources.const.RUNTIME_ERROR, 0, 0 
                
            elif os.WIFSIGNALED(status):
                ptrace.kill(pid)
                return ENUMResources.const.TIME_OVER, res[0], usingMem
            
            else:
                usingMem = self.GetUsingMemory(pid, usingMem)
                
                
                ptrace.syscall(pid, 0)
                
    def GetUsingMemory(self, pid, usingMem):
        procFileOpenCommand = "%s%i%s" % ('/proc/', pid, '/status') 
        fileLines = FileTools.ReadFileLines(procFileOpenCommand)
        split = string.split

        for i in range(15,20):
            index = fileLines[i].find('VmRSS')
            if index != -1:
                words = split(fileLines[i])
                temp = int(words[index+1])
                break;
        
        if temp > usingMem:
            usingMem = temp
        
        return usingMem
    
    def ResultError(self, result, userTime, usingMem):
        print result, 0, userTime, usingMem
        sys.exit()