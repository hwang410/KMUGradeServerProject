# -*- coding: utf-8 -*-
"""
    photolog.DB.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 DB 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR, INTEGER

from DB import Base
from DB.department import Department

class Member (Base) :
    
    __tablename__ ='Member'
    
    memberId =Column (VARCHAR (20), primary_key =True)
    password =Column (VARCHAR (50), nullable =False)
    memberName =Column (VARCHAR (20), nullable =False)
    phoneNum =Column (VARCHAR  (13), nullable =True)
    email =Column (VARCHAR  (50), nullable =True)
    authority =Column (INTEGER , default =2)
    joinDate =Column (DATETIME, nullable =False)
    accessDate =Column (DATETIME, nullable =True)
    comment =Column (VARCHAR (100), nullable =True)
    departmentNum =Column (INTEGER, 
                           ForeignKey (Department.departmentNum, 
                                       onupdate="CASCADE", ondelete ="CASCADE"), nullable =False)
    
    