# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER

from GradeServer.model import Base
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.languages import Languages

class LanguagesOfCourses (Base) :
    
    __tablename__ ="LanguagesOfCourses"
    
    courseId =Column (VARCHAR (10), ForeignKey (RegisteredCourses.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    languageIndex =Column (INTEGER (unsigned =True), ForeignKey (Languages.languageIndex, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, autoincrement =False, nullable =False)   
    