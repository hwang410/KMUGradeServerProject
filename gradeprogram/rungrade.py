import os
import logging
import sys

if __name__ == '__main__':
    # save system args for list
    args = sys.argv
    
    if len(args) != 14:
        sys.exit()
    
    from grading import InterfaceGrade
    
    logging.basicConfig(level=logging.DEBUG)
    
    logging.debug(args[2] + ' grading start')
    os.chdir('tempdir')
    
    grade = InterfaceGrade.InterfaceGrade(args)
    result, stdNum, problemNum, courseNum, submitCount = grade.Compile()
    
    if result == 'CompileError':
        # update DBManager 'compile error'
        resultMessage = "%s %i %i %i" % (result, 0, 0, 0)
        sys.stderr.write(resultMessage)
        sys.exit()
    
    result, score, runTime, usingMem = grade.Evaluation()
    
    # update DBManager 'solved'
    print result, score, runTime, usingMem