import MakePath
import CompileTools
from grading import ExecutionTools
from grading import GradingTools

class InterfaceGrade(object):
    def __init__(self, args):
        self.path = MakePath.MakePath(args)
        
    def Compile(self):
        _compile = CompileTools.CompileTools(self.path.filePath, self.path.stdNum,
                                             self.path.usingLang, self.path.version,
                                             self.path.runFileName)
        success = _compile.CodeCompile()
        
        return success, self.path.stdNum, self.path.problemNum, self.path.courseNum, self.path.submitCount
        
    def Evaluation(self):
        execution = ExecutionTools.ExecutionTools(self.path.usingLang, self.path.limitTime,
                                                 self.path.limitMemory, self.path.answerPath,
                                                 self.path.version, self.path.runFileName,
                                                 self.path.problemName, self.path.caseCount)
            
        success, runTime, usingMem = execution.Execution()
        
        if success == 'Grading':
            evaluation = GradingTools.GradingTools(self.path.gradeMethod, self.path.caseCount,
                                                   self.path.usingLang, self.path.version,
                                                   self.path.answerPath, self.path.problemName,
                                                   self.path.filePath)
             
            success = evaluation.Grade()
        
        if success == 'error':
            return 'ServerError', 0, 0
            
        return success, runTime, usingMem