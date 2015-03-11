# -*- coding: utf-8 -*-
"""
    photolog.DB.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 DB 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, DATETIME

from DB import Base
from DB.problem import Problem
from DB.member import Member
from DB.course import Course
from DB.language import Language

class Submit (Base) :
    
    __tablename__ ="Submit"
    
    memberId =Column (VARCHAR (20), ForeignKey (Member.memberId, onupdate ="CASCADE", ondelete ="CACADE"),primary_key =True)
    problemNum =Column (INTEGER, ForeignKey (Problem.problemNum, onupdate ="CASCADE"), primary_key =True, autoincrement =False)
    courseNum =Column (INTEGER, ForeignKey (Course.courseNum, onupdate ="CASCADE"), primary_key =True, autoincrement =False)
    submitCount =Column (INTEGER, primary_key =True, autoincrement =False)
    status =Column (INTEGER, default =5)
    score =Column (INTEGER, default =0)
    submitDate =Column (DATETIME, nullable =False)
    viewCount =Column (INTEGER, default =0)
    runTime =Column (INTEGER, default =0)
    usingMemory =Column (INTEGER, default =0)
    submitLanguage =Column (INTEGER, ForeignKey (Language.languageNum, onupdate ="CASCADE"), nullable =False)