import glob
from subprocess import call

class CompileTools(object):
    def __init__(self, filePath, stdNum, usingLang, version, runFileName):
        self.filePath = filePath
        self.stdNum = stdNum
        self.usingLang = usingLang
        self.version = version
        self.runFileName = runFileName
        
    def CodeCompile(self):
        if self.usingLang == 'PYTHON':
            try:
                call('cp ' + self.filePath + '*.py ./', shell = True)
            except Exception as e:
                print e
                return 'error'
            
            return True
            
        # make compile command
        command = self.MakeCommand()
        
        # code compile
        call(command, shell = True)
        
        # check compile error
        result = self.CompileErrorCheck()
        
        if result == False: # if compile error -> make error list
            result = self.MakeErrorList()
        
        # if not make execution file
        elif len(glob.glob('./'+self.runFileName)) == 0 and len(glob.glob(self.runFileName + '.class')) == 0:
            return 'error'
        
        return result
        
    def CompileErrorCheck(self):
        # if exist error message in file, compile error
        try:
            fp = open('error.err', 'r')
        except Exception as e:
            print e
            return 'error'
        
        errMess = fp.read()
        
        fp.close()
    
        if errMess.find('error:') > 0:  # if there is an 'error'
            return False
        
        return True
        
        
    def MakeErrorList(self):
        # if collect error message
        count = 0
        
        try:
            wf = open(self.filePath + 'errorlist.txt', 'w')
            rf = open('error.err', 'r')
        except Exception as e:
            print e
            return 'error'
        
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
        # make compile command 
        if self.usingLang == 'C':
            extension = 'gcc ' 
            option = '*.c -o main -lm -Wall 2>error.err'
            
        elif self.usingLang == 'C++':
            extension = 'g++ '
            option = '*.cpp -o main -lm -Wall 2>error.err'
        
        elif self.usingLang == 'JAVA':
            extension = 'javac -d ./ '  
            option = '*.java 2>error.err'
            
        return extension + self.filePath + option 