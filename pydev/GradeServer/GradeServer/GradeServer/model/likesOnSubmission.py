# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, ENUM

from GradeServer.model import Base
from GradeServer.model.submissions import Submissions
from GradeServer.model.members import Members

class LikesOnSubmission(Base) :
    
    __tablename__ ='LikesOnSubmission'
    
    memberId =Column(VARCHAR (20), ForeignKey (Submissions.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    problemId =Column(INTEGER (unsigned =True), ForeignKey (Submissions.problemId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    courseId =Column(VARCHAR (10), ForeignKey (Submissions.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    codeLikerId =Column(VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    cancelledLike =Column(ENUM ('Cancelled', 'Not-Cancelled'), default ='Not-Cancelled', nullable =False)
    
    