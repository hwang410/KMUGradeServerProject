import os
import glob
from route import AnswerRoute, FileRoute, AnswerDefaultRoute

class MakePath(object):
    def __init__(self, args):
        # save system args for var -> data type is string
        self.courseName = args[1]
        self.stdNum = args[2]
        self.problemNum = int(args[3])
        self.gradeMethod = int(args[4])
        self.limitTime = int(args[5])
        self.caseCount = int(args[6])
        self.usingLang = int(args[7])
        self.version = args[8]
        self.courseNum = int(args[9])
        self.submitCount = int(args[10])
        self.gradeCount = int(args[11])
        self.classNum = args[9][8:]

        self.runFileName = '*'
        self.defaultRoute = AnswerDefaultRoute()
        
        # basic file route set -> source code, input data
        self.problemDirectoryName = self.DirectoryName()
        self.answerRoute = self.AnswerPath()
        self.problemDirectoryName = self.DirectoryName()
        self.baseRoute = self.BasePath()
    
        # copy input data
        os.system('cp ' + self.answerRoute + self.problemDirectoryName + '_total.in input.txt')
        
        self.runFileName = self.RunFileName()
        
    def BasePath(self):
        return FileRoute(self.courseName, self.classNum, self.stdNum, self.problemDirectoryName)
    
    def AnswerPath(self):
        path = AnswerRoute(self.problemDirectoryName)
        
        if self.gradeMethod == 0:
            return path + 'solution/'
        else:
            return path + 'check/'
    
    def RunFileName(self):
        if self.courseNum == 0:
            count = glob.glob(self.answerRoute + '*.py')
        elif self.courseNum == 3:
            count = glob.glob(self.answerRoute + '*.java')
        else:
            return '*'
            
        if len(count) > 1:
            return 'main'
        else:
            return '*'
        
    def DirectoryName(self):
        dirName = glob.glob(self.defaultRoute + str(self.problemNum) + '_*')
        name = dirName[0].split('/')
        return name[-1]