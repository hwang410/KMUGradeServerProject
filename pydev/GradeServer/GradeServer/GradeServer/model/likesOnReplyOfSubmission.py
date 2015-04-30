# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog �뼱�뵆由ъ��씠�뀡�쓣 �궗�슜�븷 �궗�슜�옄 �젙蹂댁뿉 ���븳 model 紐⑤뱢.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, ENUM

from GradeServer.model import Base
from GradeServer.model.repliesOnSubmission import RepliesOnSubmission
from GradeServer.model.members import Members
from GradeServer.resource.enumResources import ENUMResources

class LikesOnReplyOfSubmission (Base) :
    
    __tablename__ ="LikesOnReplyOfSubmission"
    
    submitReplyIndex =Column (INTEGER (unsigned =True), ForeignKey (RepliesOnSubmission.submissionReplyIndex, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    codeWriterId =Column (VARCHAR (20), ForeignKey (RepliesOnSubmission.codeWriterId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    problemId =Column (INTEGER (unsigned =True), ForeignKey (RepliesOnSubmission.problemId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    courseId =Column (VARCHAR (10), ForeignKey (RepliesOnSubmission.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    codeReplyLikerId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    isLikeCancelled =Column (ENUM (ENUMResources().const.true,
                                 ENUMResources().const.false),
                           default = ENUMResources().const.false,
                           nullable =False)
    