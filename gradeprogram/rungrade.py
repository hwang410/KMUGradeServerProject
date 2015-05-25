import os
import sys
import logging
from gradingResource.enumResources import ENUMResources

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    # save system args for list
    args = sys.argv
    
    if len(args) != 11:
        print ENUMResources.const.SERVER_ERROR, 0, 0, 0
        sys.exit()
    
    from grading import InterfaceGrade
    
    logging.debug(args[3] + ' grading start')
    os.chdir('tempdir')

    grade = InterfaceGrade.InterfaceGrade(args)
    result = grade.Compile()
    
    if result == ENUMResources.const.COMPILE_ERROR:
        # update DBManager 'compile error'
        print result, 0, 0, 0
        sys.exit()
    
    result, score, runTime, usingMem = grade.Evaluation()