# -*- coding: utf-8 -*-
"""
    photolog.DB.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 DB 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR, INTEGER, TEXT

from DB import Base
from DB.language import Language

class Course (Base) :
    
    __tablename__ ="Course"
    
    courseNum =Column (INTEGER, primary_key =True)
    courseName =Column (VARCHAR (30), nullable =False)
    defaultLanguage =Column (INTEGER, ForeignKey (Language.languageNum, onupdate ="CASCADE", ondelete ="CASCADE"), nullable =True)
    courseInformation =Column (TEXT, nullable =True)
    beginDate =Column (DATETIME, nullable =True)
    dueDate =Column (DATETIME, nullable =True)
    memberId =Column (VARCHAR (20), nullable =False)
    