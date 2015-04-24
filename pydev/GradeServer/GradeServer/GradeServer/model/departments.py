# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, ENUM

from GradeServer.model import Base
from GradeServer.resource.enumResources import ENUMResources

class Departments(Base) :
    
    __tablename__ ='Departments'
    
    departmentIndex =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =True, nullable =False)
    departmentCode =Column (VARCHAR (128), nullable =False)
    departmentName =Column (VARCHAR (1024), nullable =False)
    isAbolished =Column (ENUM (ENUMResources.const.TRUE,
                               ENUMResources.const.FALSE),
                         default = ENUMResources.const.FALSE,
                         nullable =False)
    