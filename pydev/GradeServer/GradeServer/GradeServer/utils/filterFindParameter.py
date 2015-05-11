# -*- coding: utf-8 -*-
"""
    GradeServer.utils
    ~~~~~~~~~~~~~~

    GradeSever에 적용될 FilterFindParameter 대한 패키지 초기화 모듈.

    :copyright: (c) 2015 kookminUniv
    :@author: algolab
"""
    
class FilterFindParameter:
    # filterCondition
    filterCondition = None
    keyWord = ''
    
    def __init__(self, filterCondition = None, keyWord = ''):
        self.filterCondition = filterCondition
        self.keyWord = keyWord