# -*- coding: utf-8 -*-
"""
    GradeServer.utils
    ~~~~~~~~~~~~~~

    GradeSever에 적용될   MemberCourseProblemParameter 대한 패키지 초기화 모듈.

    :copyright: (c) 2015 kookminUniv
    :@author: algolab
"""
    
class MemberCourseProblemParameter:
    # filterCondition
    memberId = None
    courseId = None
    problemId = None
    
    def __init__(self, memberId = None, courseId = None, problemId = None):
        self.memberId = memberId
        self.courseId = courseId
        self.problemId = problemId