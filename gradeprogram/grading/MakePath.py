import glob

class MakePath(object):
    def __init__(self, args):
        # save system args for var -> data type is string
        self.filePath = args[1]
        self.problemPath = args[2]
        self.stdNum = args[3]
        self.problemNum = int(args[4])
        self.gradeMethod = args[5]
        self.caseCount = int(args[6])
        self.limitTime = int(args[7])
        self.limitMemory = int(args[8])
        self.usingLang = args[9]
        self.version = args[10]
        self.courseNum = int(args[11])
        self.submitCount = int(args[12])
        
        # catch problemName
        self.problemName = self.ProblemName()
        
        # make execution file name
        self.runFileName = self.RunFileName()
        
        self.filePath = self.filePath + '/'
        self.answerPath = self.AnswerPath()
    
    def AnswerPath(self):
        if self.gradeMethod == 'Solution':
            return self.problemPath + '/' + self.problemName + '_Solution/'
        else:
            return self.problemPath + '/' + self.problemName + '_Checker/'
    
    def RunFileName(self):
        if self.usingLang == 'PYTHON':
            fileList = glob.glob(self.filePath + '*.py')
        elif self.usingLang == 'JAVA':
            fileList = glob.glob(self.filePath + '*.java')
        else:
            return 'main'
            
        if len(fileList) > 1:
            return 'main'
        else:
            name = fileList[0].split('/')[-1]
            return name.split('.')[0]
        
    def ProblemName(self):
        return self.problemPath.split('/')[-1]