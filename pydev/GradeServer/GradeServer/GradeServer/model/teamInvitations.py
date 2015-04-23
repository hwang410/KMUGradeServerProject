# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, ENUM

from GradeServer.model import Base
from GradeServer.model.members import Members
from GradeServer.model.teams import Teams

from GradeServer.utils.enumResources import ENUMResources

class TeamInvitations (Base) :
    
    __tablename__ ="TeamInvitations"
    
    teamName =Column (VARCHAR (128), ForeignKey (Teams.teamName, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    inviteeId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    isDeleted =Column (ENUM (ENUMResources.const.true,
                             ENUMResources.const.false),
                       default = ENUMResources.const.false,
                       nullable =False)