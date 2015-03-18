# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, DATETIME, VARCHAR, ENUM

from DB import Base
from DB.problems import Problems
from DB.registeredCourses import RegisteredCourses

class RegisteredProblems (Base) :
    
    __tablename__ ="RegisteredProblems"
    
    problemId =Column (INTEGER, ForeignKey (Problems.problemIndex, onupdate ="CASCADE", ondelete ="CASCADE"), autoincrement =False, primary_key =True, nullable =False)
    courseId =Column (VARCHAR (10), ForeignKey (RegisteredCourses.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    solutionCheckType =Column (ENUM ('Solution', 'Checker'), default ='Solution', nullable =False)
    isAllInputCaseInOneFile =Column (ENUM ('OneFile', 'MultipleFiles'), default ='OneFile', nullable =False)
    limittedFileSize =Column (INTEGER (unsigned =True), default =1024, nullable =False) #MB
    openDate =Column (DATETIME, nullable =False)
    closeDate =Column (DATETIME, nullable =False)
    startDateOfSubmission =Column (DATETIME, nullable =False)
    endDateOfSubmission =Column (DATETIME, nullable =False)
    