from gradingResource.listResources import ListResources

class GradingCommand(object):
    @staticmethod
    def MakeCompileCommand(usingLang, filePath):
        # make compile command 
        if usingLang == ListResources.const.Lang_C:
            return "%s%s%s" % ('gcc ', filePath, '*.c -o main -lm -w 2>error.err')
            
        elif usingLang == ListResources.const.Lang_CPP:
            return "%s%s%s" % ('g++ ', filePath, '*.cpp -o main -lm -w 2>error.err')
        
        elif usingLang == ListResources.const.Lang_JAVA:
            return "%s%s%s" % ('javac -nowarn -d ./ ', filePath, '*.java 2>error.err')
        
    @staticmethod
    def MakeExecuteCommand(usingLang, runFileName, version):
        # make execution command
        runCommandList = []
        append = runCommandList.append
        
        if usingLang == ListResources.const.Lang_PYTHON:
            if version == ListResources.const.PYTHON_VERSION_TWO:
                append('/usr/bin/python')
                append('/usr/bin/python')
                append(runFileName + '.py')
                
            elif version == ListResources.const.PYTHON_VERSION_THREE:
                append('/usr/local/bin/python3')
                append('/usr/local/bin/python3')
                append(runFileName + '.py')
                
        elif usingLang == ListResources.const.Lang_C or usingLang == ListResources.const.Lang_CPP:
            append('./main')
            append('./main')
            
        elif usingLang == ListResources.const.Lang_JAVA:
            append('/usr/bin/java')
            append('/usr/bin/java')
            append(runFileName)
            
        return runCommandList
    
    @staticmethod
    def MakeMulticaseCommand(usingLag, version):
        # make execution command
        if usingLang == ListResources.const.Lang_PYTHON:
            if version == ListResources.const.PYTHON_VERSION_TWO:
                return "%s%s%s" % ('python ', runFileName, '.py 1>output.txt 2>core.1')
            elif version == ListResources.const.PYTHON_VERSION_THREE:
                return "%s%s%s" % ('python3 ', runFileName, '.py 1>output.txt 2>core.1')
        
        elif usingLang == ListResources.const.Lang_C or usingLang == ListResources.const.Lang_CPP:
            return './main 1>output.txt'
        
        elif usingLang == ListResources.const.Lang_JAVA:
            return "%s%s%s" % ('java ', runFileName, ' 1>output.txt 2>core.1')