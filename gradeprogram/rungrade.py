import os
import sys

if __name__ == '__main__':
    # save system args for list
    args = sys.argv
    
    if len(args) != 14:
        sys.exit()
    
    from grading import InterfaceGrade
    
    os.chdir('tempdir')
    
    grade = InterfaceGrade.InterfaceGrade(args)
    result, stdNum, problemNum, courseNum, submitCount = grade.Compile()
    
    if result == 'CompileError':
        # update DBManager 'compile error'
        print result, 0, 0, 0
        sys.exit()
    
    result, score, runTime, usingMem = grade.Evaluation()
    
    # update DBManager 'solved'
    print result, score, runTime, usingMem