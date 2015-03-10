# -*- coding: utf-8 -*-
"""
    photolog.DB.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 DB 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER

from DB import Base

class Department(Base) :
    
    __tablename__ ='Department'
    
    departmentNum =Column (INTEGER, primary_key =True)
    departmentName =Column (VARCHAR (20), nullable =False)