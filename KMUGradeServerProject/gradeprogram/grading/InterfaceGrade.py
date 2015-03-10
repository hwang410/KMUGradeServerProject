import MakePath
import CompileTools
import EvaluateTools
import EvaluateTools_Multicase

class InterfaceGrade(object):
    def __init__(self, args):
        self.path = MakePath.MakePath(args)
        
    def Compile(self):
        if self.path.usingLang != 0:    # if not python
            _compile = CompileTools.CompileTools(self.path.baseRoute, self.path.stdNum, self.path.usingLang,\
                                                 self.path.version, self.path.runFileName)
            success = _compile.CodeCompile()
        
        else:   # if python
            success = True
        
        return success, self.path.stdNum, self.path.problemNum, self.path.courseNum, self.path.submitCount, self.path.gradeCount
        
    def Evaluation(self):
        if self.path.caseCount == 1:    # if one testcase
            evaluation = EvaluateTools.EvaluateTools(self.path.stdNum, self.path.usingLang, self.path.limitTime, self.path.answerRoute,\
                                                     self.path.version, self.path.gradeMethod, self.path.runFileName, self.path.problemDirectoryName)
            success, runTime = evaluation.Execution()
        
        else:   # if many testcases 
            evaluation = EvaluateTools_Multicase.EvaluateTools_multicase(self.path.stdNum, self.path.usingLang, self.path.limitTime,\
                                                                         self.path.answerRoute, self.path.version, self.path.gradeMethod,\
                                                                         self.path.caseCount, self.path.runFileName, self.path.problemDirectoryName)
            success, runTime = evaluation.Execution()
            
        return success, runTime