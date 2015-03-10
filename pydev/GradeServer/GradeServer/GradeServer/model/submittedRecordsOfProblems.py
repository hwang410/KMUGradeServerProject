# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR

from GradeServer.model import Base
from GradeServer.model.problems import Problems
from GradeServer.model.registeredCourses import RegisteredCourses

class SubmittedRecordsOfProblems (Base) :
    
    __tablename__ ="SubmittedRecordsOfProblems"
    
    problemId =Column (INTEGER (unsigned =True), ForeignKey (Problems.problemId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    courseId =Column (VARCHAR (10), ForeignKey (RegisteredCourses.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    sumOfSubmissionCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    sumOfSolvedCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    sumOfWrongCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    sumOfRuntimeErrorCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    sumOfCompileErrorCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    sumOfTimeOverCount =Column (INTEGER (unsigned =True), default =0, nullable =False)