

class OtherResources(object):
    """Other Resource Static Class"""
    
    from GradeServer.resource import const
    
    # Integer
    const.NOTICE_LIST = 5
    const.BLOCK = 3
    const.LIST = 3

    const.ACCEPT = 'accept'
    const.REJECT = 'reject'
    
    const.SUBMISSION_DATE = 'submissionDate'
    const.RUN_TIME = 'runTime'
    const.USED_MEMORY = 'usedMemory'
    const.CODE_LENGTH = 'codeLength'
    
    const.RATE = 'rate'
    const.SOLVED_PROBLEM = 'solvedProblem'
    
    const.ALL = 'All'
    const.GET_FILES = 'file[]'
    const.USED_LANGUAGE_NAME = 'usedLanguageName'
    const.GET_CODE = 'getCode'
    const.LANGUAGE = 'language'
    const.C = 'C'
    const.CPP = 'C++'
    const.JAVA = 'JAVA'
    const.PYTHON = 'PYTHON'
    const.C_SOURCE_NAME = 'test.c'
    const.CPP_SOURCE_NAME = 'test.cpp'
    const.JAVA_SOURCE_NAME = '%s.java'
    const.MISS_CLASS_NAME = 'missClassName.java'
    const.PYTHON_SOURCE_NAME = 'test.py'
    const.JAVA_MAIN_CLASS = r'public\s+class\s+(\w+)'
    const.LINUX_NEW_LINE = '\r\n'
    const.WINDOWS_NEW_LINE = '\n'
    const.SUBMISSION_COUNT = 'submissionCount'
    const.SOLUTION_CHECK_COUNT = 'solutionCheckCount'
    const.SUBMISSION_SUCCESS = 'Submission Success!'
