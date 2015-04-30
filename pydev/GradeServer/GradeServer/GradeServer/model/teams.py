# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, ENUM

from GradeServer.model import Base
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.resource.enumResources import ENUMResources

class Teams (Base) :
    
    __tablename__ ="Teams"
    
    teamName =Column (VARCHAR (128), primary_key =True, nullable =False)
    courseId = Column(VARCHAR(10),
                      ForeignKey(RegisteredCourses.courseId,
                                 onupdate ="CASCADE",
                                 ondelete ="CASCADE"),
                      nullable = False)
    teamDescription =Column (TEXT, nullable =True)
    isDeleted =Column (ENUM (ENUMResources().const.TRUE,
                             ENUMResources().const.FALSE),
                       default = ENUMResources().const.FALSE,
                       nullable =False)
    