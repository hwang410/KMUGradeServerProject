import sys
import logging
from grading import ParameterSetting
import CompileTools
from grading import ExecutionTools
from grading import GradingTools

class InterfaceGrade(object):
    def __init__(self, args):
        self.parameter = ParameterSetting.ParameterSetting(args)
        
        
    def Compile(self):
        logging.debug(self.parameter.saveDirectoryName + ' compile start')
        _compile = CompileTools.CompileTools(self.parameter.filePath, self.parameter.usingLang,
                                             self.parameter.version, self.parameter.runFileName)
        success = _compile.CompileCode()
        
        logging.debug(self.parameter.saveDirectoryName + ' compile end')
        
        return success
        
    def Evaluation(self):
        score = 0
        logging.debug(self.parameter.saveDirectoryName + ' execution start')
        
        execution = ExecutionTools.ExecutionTools(self.parameter)
            
        success, runTime, usingMem = execution.Execution()
        logging.debug(self.parameter.saveDirectoryName + ' execution end')
        
        if success == 'Grading':
            logging.debug(self.parameter.saveDirectoryName + ' grade start')
            evaluation = GradingTools.GradingTools(self.parameter)
             
            success, score = evaluation.Grade()
            logging.debug(self.parameter.saveDirectoryName + ' grade end')
            
        print success, score, runTime, usingMem
        sys.exit()