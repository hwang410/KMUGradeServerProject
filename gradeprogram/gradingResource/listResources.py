

class ListResources(object):
    """ENUM Resource Static Class"""
    
    import const
    
    const.Lang_List = ['PYTHON', 'C', 'C++', 'JAVA']
    const.Lang_C = 'C'
    const.Lang_CPP = 'C++'
    const.Lang_JAVA = 'JAVA'
    const.Lang_PYTHON = 'PYTHON'
    
    const.Lang_VERSION_ZERO = '0'
    const.PYTHON_VERSION_TWO = '2.7'
    const.PYTHON_VERSION_THREE = '3.4'
    
    const.GRADERESULT_List = ['grading status', 'NEVER_SUBMITTED', 'JUDGING',
                              'SOLVED', 'TIME_OVER', 'WRONG_ANSWER', 'COMPILE_ERROR',
                              'RUNTIME_ERROR', 'SERVER_ERROR']