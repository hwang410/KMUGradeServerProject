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
from GradeServer.model.repliesOnBoard import RepliesOnBoard
from GradeServer.model.members import Members
from GradeServer.resource.enumResources import ENUMResources

class LikesOnReplyOfBoard (Base) :
    
    __tablename__ ="LikesOnReplyOfBoard"
    
    articleIndex =Column (INTEGER (unsigned =True), ForeignKey (RepliesOnBoard.articleIndex, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    boardReplyIndex =Column (INTEGER (unsigned =True), ForeignKey (RepliesOnBoard.boardReplyIndex, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    boardReplyLikerId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    isLikeCancelled =Column (ENUM (ENUMResources.const.TRUE,
                                   ENUMResources.const.FALSE),
                             default = ENUMResources.const.FALSE,
                             nullable =False)