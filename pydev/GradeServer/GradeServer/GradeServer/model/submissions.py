# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, DATETIME, ENUM

from GradeServer.model import Base
from GradeServer.model.languages import Languages
from GradeServer.model.submittedFiles import SubmittedFiles

from GradeServer.resource.enumResources import ENUMResources

class Submissions (Base) :
    
    __tablename__ ="Submissions"
    
    memberId =Column (VARCHAR (20), ForeignKey (SubmittedFiles.memberId, onupdate ="CASCADE", ondelete ="CACADE"),primary_key =True, nullable =False)
    problemId =Column (INTEGER (unsigned =True), ForeignKey (SubmittedFiles.problemId, onupdate ="CASCADE", ondelete ="NO ACTION"), primary_key =True, autoincrement =False, nullable = False)
    courseId =Column (VARCHAR (10), ForeignKey (SubmittedFiles.courseId, onupdate ="CASCADE", ondelete ="NO ACTION"), primary_key =True, nullable = False)
    submissionCount =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =False, default =0, nullable =False)
    solutionCheckCount =Column (INTEGER (unsigned =True), default = 0, nullable =False)
    status =Column (ENUM (ENUMResources.const.NEVER_SUBMITTED,
                          ENUMResources.const.JUDGING,
                          ENUMResources.const.SOLVED,
                          ENUMResources.const.TIME_OVER,
                          ENUMResources.const.WRONG_ANSWER,
                          ENUMResources.const.COMPILE_ERROR,
                          ENUMResources.const.RUNTIME_ERROR,
                          ENUMResources.const.SERVER_ERROR),
                    default = ENUMResources.const.NEVER_SUBMITTED,
                    nullable =False)
    score =Column (INTEGER (unsigned =True), default =0, nullable =False)
    codeSubmissionDate =Column (DATETIME, nullable =False)
    viewCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    sumOfSubmittedFileSize =Column (INTEGER (unsigned =True), nullable =False) # Byte
    runTime =Column (INTEGER (unsigned =True), default =0, nullable =False)
    usedMemory =Column (INTEGER (unsigned =True), default =0, nullable =False)
    usedLanguageIndex =Column (INTEGER (unsigned =True), ForeignKey (Languages.languageIndex, onupdate="CASCADE", ondelete ="NO ACTION"), nullable =False)
    