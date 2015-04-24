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
from GradeServer.model.members import Members
from GradeServer.model.submissions import Submissions

from GradeServer.resource.enumResources import ENUMResources

class RepliesOnSubmission (Base) :
    
    __tablename__ ="RepliesOnSubmission"
    
    submissionReplyIndex =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =False, nullable =False)
    codeWriterId =Column (VARCHAR (20), ForeignKey (Submissions.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    problemId =Column (INTEGER (unsigned =True), ForeignKey (Submissions.problemId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    courseId =Column (VARCHAR (10), ForeignKey (Submissions.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    codeReplierId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =False)
    codeReplyContent =Column (TEXT, nullable =False)
    codeReplierIp =Column (VARCHAR (20), nullable =False)
    codeRepliedDate =Column (DATETIME, nullable =False)
    isDeleted =Column (ENUM (ENUMResources.const.true,
                             ENUMResources.const.false),
                       default = ENUMResources.const.false,
                       nullable =False)
    sumOfLikeCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    