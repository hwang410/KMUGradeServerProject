# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, DATETIME

from GradeServer.model import Base
from GradeServer.model.members import Members

class ServerLogs (Base) :
    
    __tablename__ ="ServerLogs"
    
    logIndex =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =True)
    loggedDate =Column (DATETIME, nullable =False)
    serverStatus =Column (INTEGER (unsigned =True), nullaable =False)
    memberId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="NO ACTION"), nullable =False)
    