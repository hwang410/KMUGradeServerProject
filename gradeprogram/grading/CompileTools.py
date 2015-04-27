import glob
import string
import DBUpdate
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
                copyCommand = "%s%s%s" % ('cp ', self.filePath, '*.py ./')
                call(copyCommand, shell = True)
            except Exception as e:
                print 'compile python file copy'
                DBUpdate.SubmittedRecordsOfProblems()
            
            return True
            
        # make compile command
        command = self.MakeCommand()
        
        # code compile
        call(command, shell = True)
        
        # check compile error
        result = self.CompileErrorCheck()
        
        if result == 'CompileError': # if compile error -> make error list
            result = self.MakeErrorList()
        
        # if not make execution file
        elif len(glob.glob('./'+self.runFileName)) == 0 and len(glob.glob(self.runFileName + '.class')) == 0:
            DBUpdate.SubmittedRecordsOfProblems()
        
        return result
        
    def CompileErrorCheck(self):
        # if exist error message in file, compile error
        try:
            fp = open('error.err', 'r')
        except Exception as e:
            print 'compile error check file open error'
            DBUpdate.SubmittedRecordsOfProblems()
        
        errMess = fp.read()
        
        fp.close()
    
        if errMess.find('error:') > 0:  # if there is an 'error'
            return 'CompileError'
        
        return True
        
        
    def MakeErrorList(self):
        # if collect error message
        count = 0
        
        try:
            wf = open(self.filePath + 'errorlist.txt', 'w')
            rf = open('error.err', 'r')
        except Exception as e:
            print 'make compile error list file open error'
            DBUpdate.SubmittedRecordsOfProblems()
        
        lines = rf.readlines()
        _list = []
        append = _list.append
        
        split = string.split
        
        for line in lines:
            if line.find('error:') != -1:   # if there is an 'error:'
                part = split(line, '/')
                append(part[-1])
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
            return "%s%s%s" % ('gcc ', self.filePath, '*.c -o main -lm -w 2>error.err')
            
        elif self.usingLang == 'C++':
            return "%s%s%s" % ('g++', self.filePath, '*.cpp -o main -lm -w 2>error.err')
        
        elif self.usingLang == 'JAVA':
            return "%s%s%s" % ('javac -nowarn -d ./', self.filePath, '*.java 2>error.err')