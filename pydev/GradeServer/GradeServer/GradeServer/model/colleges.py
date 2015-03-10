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

class Colleges (Base) :
    
    __tablename__ ='Colleges'
    
    collegeIndex =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =True, nullable =False)
    collegeCode =Column (VARCHAR (128), nullable =False)
    collegeName =Column (VARCHAR (1024), nullable =False)
    isAbolished =Column (ENUM ('Abolished', 'Not-Abolished'), default ='Not-Abolished', nullable =False)
    