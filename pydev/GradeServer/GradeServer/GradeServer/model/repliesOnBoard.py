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
from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.members import Members

from GradeServer.utils.enumResources import ENUMResources

class RepliesOnBoard (Base) :
    
    __tablename__ ="RepliesOnBoard"
    
    boardReplyIndex =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =False, nullable =False)
    articleIndex =Column (INTEGER (unsigned =True), ForeignKey (ArticlesOnBoard.articleIndex, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    boardReplierId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =False)
    boardReplyContent =Column (TEXT, nullable =False)
    boardReplierIp =Column (VARCHAR (20), nullable =False)
    boardRepliedDate =Column (DATETIME, nullable =False)
    isDeleted =Column (ENUM (ENUMResources.const.true,
                             ENUMResources.const.false),
                       default = ENUMResources.const.false,
                       nullable =False)
    sumOfLikeCount =Column (INTEGER (unsigned =True), default =0, nullable =False)
    