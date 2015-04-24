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
from GradeServer.model.members import Members
from GradeServer.model.departmentsOfColleges import DepartmentsOfColleges

class DepartmentsDetailsOfMembers(Base) :
    
    __tablename__ ='DepartmentsDetailsOfMembers'
    
    memberId =Column (VARCHAR (20),
                      ForeignKey(Members.memberId,
                                 onupdate ="CASCADE",
                                 ondelete ="CASCADE"),
                                 primary_key =True,
                                 nullable =False)
    collegeIndex =Column (INTEGER (unsigned =True), ForeignKey (DepartmentsOfColleges.collegeIndex, onupdate ="CASCADE", ondelete ="NO ACTION"), primary_key =True, nullable =False)
    departmentIndex =Column (INTEGER (unsigned =True), ForeignKey (DepartmentsOfColleges.departmentIndex, onupdate="CASCADE", ondelete ="NO ACTION"), primary_key =True, nullable =False)