# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR

from GradeServer.model import Base
from GradeServer.model.members import Members
from GradeServer.model.registeredCourses import RegisteredCourses

class Registrations (Base) :
    
    __tablename__ ="Registrations"
    
    memberId =Column (VARCHAR (20), ForeignKey (Members.memberId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    courseId =Column (VARCHAR (10), ForeignKey (RegisteredCourses.courseId, onupdate ="CASCADE", ondelete ="CASCADE"), primary_key =True, nullable =False)
    