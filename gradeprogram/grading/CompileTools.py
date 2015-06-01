import os
import sys
import glob
import string
from subprocess import call
from FileTools import FileTools
from GradingCommand import GradingCommand
from gradingResource.listResources import ListResources
from gradingResource.enumResources import ENUMResources

class CompileTools(object):
    def __init__(self, filePath, usingLang, version, runFileName):
        self.filePath = filePath
        self.usingLang = usingLang
        self.version = version
        self.runFileName = runFileName
        
    def CompileCode(self):
        if self.usingLang == ListResources.const.Lang_PYTHON:
            copyCommand = "%s%s%s" % ('cp ', self.filePath, '*.py ./')
            call(copyCommand, shell = True)
            
            if len(glob.glob('*.py')) == 0:
                print 'compile python file copy'
                print ENUMResources.const.SERVER_ERROR, 0, 0, 0
                sys.exit()
            
            return True
            
        # make compile command
        command = GradingCommand.MakeCompileCommand(self.usingLang, self.filePath)
        
        # code compile
        call(command, shell = True)
        
        # check compile error
        if os.path.getsize('error.err') > 0:
            self.MakeErrorList()
            print ENUMResources.const.COMPILE_ERROR, 0, 0, 0
            sys.exit()
        
        # if not make execution file
        elif os.path.exists(self.runFileName) or os.path.exists(self.runFileName + '.class'):
            return True
        
        else:
            print ENUMResources.const.SERVER_ERROR, 0, 0, 0
            sys.exit()
        
        
    def MakeErrorList(self):
        # if collect error message
        count = 0
        
        try:
            wf = open('errorlist.txt', 'w')
        except Exception as e:
            print 'make compile error list file open error'
            print ENUMResources.const.COMPILE_ERROR, 0, 0, 0
            sys.exit()
        
        lines = FileTools.ReadFileLines('error.err')
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