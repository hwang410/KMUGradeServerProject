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
        self.problemName = self.MakeProblemName()
        
        # make execution file name
        self.filePath = self.filePath + '/'
        self.runFileName = self.MakeRunFileName()
        
        self.answerPath = self.MakeAnswerPath()
    
    def MakeAnswerPath(self):
        return self.problemPath + '/' + self.problemName + '_' + self.gradeMethod + '/'
    
    def MakeRunFileName(self):
        if self.usingLang == 'C' or self.usingLang == 'C++':
            return 'main'
        
        if self.usingLang == 'JAVA':
            fileExtention = '*.java'
            
        else:
            fileExtention = '*.py'
            
        fileList = glob.glob(self.filePath + fileExtention)
        
        if fileList:
            return 'main'
        
        name = fileList[0].split('/')[-1]
        return name.split('.')[0]
        
    def MakeProblemName(self):
        return self.problemPath.split('/')[-1]