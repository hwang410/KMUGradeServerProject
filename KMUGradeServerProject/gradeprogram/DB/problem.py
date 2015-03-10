# -*- coding: utf-8 -*-
"""
    photolog.DB.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 DB 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, TEXT

from DB import Base
from DB.problemType import ProblemType
from DB.member import Member 

class Problem (Base) :
    
    __tablename__ ="Problem"
    
    problemNum =Column (INTEGER, primary_key =True)
    problemName =Column (VARCHAR (30), nullable =False)
    typeNum =Column (INTEGER, ForeignKey (ProblemType.typeNum, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =False)
    checkType =Column (INTEGER, default =0)
    limitTime =Column (INTEGER, default =3)
    uploader =Column (VARCHAR (20), ForeignKey (Member.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =False)
    limitMemory =Column (INTEGER, default =1024)
    problemContent =Column (TEXT, nullable =True)