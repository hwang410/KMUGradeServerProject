# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column 
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, TEXT, ENUM

from DB import Base 

class Problems (Base) :
    
    __tablename__ ="Problems"
    
    problemIndex = Column (INTEGER (unsigned =True), nullable =False)
    problemId =Column (INTEGER (unsigned =True), primary_key =True, autoincrement =False, nullable =False)
    problemName =Column (VARCHAR (1024), nullable =False)
    solutionCheckType =Column (ENUM ('Solution', 'Checker'), default ='Solution', nullable =False)
    limitedTime =Column (INTEGER (unsigned =True), default =3000, nullable =False) #ms
    limitedMemory =Column (INTEGER (unsigned =True), default =1024, nullable =False) #MB
    problemPath =Column (TEXT, nullable =True)
    isDeleted =Column (ENUM ('TRUE', 'FALSE'), default ='FALSE', nullable =False)