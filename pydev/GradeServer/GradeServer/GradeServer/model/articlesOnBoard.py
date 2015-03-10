# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, DATETIME, TEXT, ENUM

from GradeServer.model import Base
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.members import Members
from GradeServer.model.problems import Problems

class ArticlesOnBoard (Base) :
    
    __tablename__ ="ArticlesOnBoard"
    
    articleIndex =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =True, nullable =False) 
    isNotice =Column (ENUM ('Notice', 'Not-Notice'), default ='Not-Notice', nullable =False)    # checker for notice
    writerId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =False)
    problemId =Column (INTEGER (unsigned =True), ForeignKey (Problems.problemId, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =True)
    courseId =Column (VARCHAR (10), ForeignKey (RegisteredCourses.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =False)
    title =Column (VARCHAR (1024), nullable =False)
    content =Column (TEXT, nullable =False) # contents of article
    viewCount =Column (INTEGER (unsigned =True), default =0, nullable =False) 
    replyCount =Column (INTEGER, default =0, nullable =False)
    writerIp =Column (VARCHAR (20), nullable =False)
    writtenDate =Column (DATETIME, nullable =False)
    isDeleted =Column (ENUM ('Deleted', 'Not-Deleted'), default ='Not-Deleted', nullable =False)
    sumOfLikeCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    