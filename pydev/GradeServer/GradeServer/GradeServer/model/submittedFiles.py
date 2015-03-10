# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, TEXT

from GradeServer.model import Base
from GradeServer.model.members import Members
from GradeServer.model.registeredProblems import RegisteredProblems

class SubmittedFiles (Base) :
    
    __tablename__ ="SubmittedFiles"
    
    memberId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    problemId =Column (INTEGER (unsigned =True), ForeignKey (RegisteredProblems.problemId, ondelete ="NO ACTION"), autoincrement =False, primary_key =True, nullable =False)
    courseId =Column (VARCHAR (20), ForeignKey (RegisteredProblems.courseId, onupdate ="CASCADE", ondelete ="NO ACTION"), primary_key =True, nullable =False)
    fileIndex =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =False, nullable =False)
    fileName =Column (VARCHAR (50), nullable =False)
    filePath =Column (TEXT, nullable =False)
    fileSize =Column (INTEGER (unsigned =True), default =0, nullable =False) #Byte
