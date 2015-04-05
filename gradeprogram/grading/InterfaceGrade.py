import MakePath
import CompileTools
import EvaluateTools
import EvaluateTools_Multicase

class InterfaceGrade(object):
    def __init__(self, args):
        self.path = MakePath.MakePath(args)
        
    def Compile(self):
        _compile = CompileTools.CompileTools(self.path.filePath, self.path.stdNum, self.path.usingLang, self.path.version, self.path.runFileName)
        success = _compile.CodeCompile()
        
        return success, self.path.stdNum, self.path.problemNum, self.path.courseNum, self.path.submitCount
        
    def Evaluation(self):
        if self.path.caseCount < 2:    # if one testcase
            evaluation = EvaluateTools.EvaluateTools(self.path.usingLang, self.path.limitTime, self.path.limitMemory, self.path.answerPath,\
                                                     self.path.version, self.path.gradeMethod, self.path.runFileName, self.path.problemName,\
                                                     self.path.caseCount)
            
            success, runTime, usingMem = evaluation.Execution()
        
        else:   # if many testcases 
            evaluation = EvaluateTools_Multicase.EvaluateTools_multicase(self.path.usingLang, self.path.limitTime, self.path.limitMemory,\
                                                                         self.path.answerPath, self.path.version, self.path.gradeMethod,\
                                                                         self.path.caseCount, self.path.runFileName, self.path.problemName,\
                                                                         self.path.filePath)
            success, runTime, usingMem = evaluation.Execution()
            
        return success, runTime, usingMem