import os
import glob

class CompileTools(object):
    def __init__(self, baseRoute, stdNum, usingLang, version, runFileName):
        self.baseRoute = baseRoute
        self.stdNum = stdNum
        self.usingLang = usingLang
        self.version = version
        self.runFileName = runFileName
        
    def CodeCompile(self):
        command = self.MakeCommand()
        os.system(command)
        result = self.CompileErrorCheck()
        
        if result == False: # if compile error
            self.MakeErrorList()
        
        elif len(glob.glob('./'+self.stdNum)) == 0 and len(glob.glob(self.runFileName + '.class')) == 0:
            return 'error'
        
        return result
        
    def CompileErrorCheck(self):
        fp = open('error.err', 'r')
        errMess = fp.read()
    
        if errMess.find('error:') > 0:  # if there is an 'error'
            return False
    
        return True
        
        
    def MakeErrorList(self):
        count = 0
        wf = open('errorlist.txt', 'w')
        rf = open('error.err', 'r')
        
        lines = rf.readlines()
        _list = []
        
        for line in lines:
            if line.find('error:') != -1:   # if there is an 'error:'
                part = line.split('/')
                _list.append(part[-1])
                count += 1
                if count == 6:
                    break
        
        wf.write(str(count)+'\n')
        
        wf.writelines(_list)
                
        wf.close()
        rf.close()
        
    def MakeCommand(self):
        if self.usingLang == 1:
            return 'gcc ' + self.baseRoute + '*.c -o ' + self.stdNum + ' -O2 -lm -Wall 2>error.err'
            
        elif self.usingLang == 2:
            return 'g++ ' + self.baseRoute + '*.c -o ' + self.stdNum + ' -O2 -lm -Wall 2>error.err'
        
        elif self.usingLang == 3:
            return 'javac *.java 2>error.err'