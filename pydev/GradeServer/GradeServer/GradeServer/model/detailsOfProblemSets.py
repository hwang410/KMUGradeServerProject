# -*- coding: utf-8 -*-
"""
    photolog.model.photo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    photolog 어플리케이션을 사용할 사용자 정보에 대한 model 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER

from GradeServer.model import Base
from GradeServer.model.problems import Problems
from GradeServer.model.problemSets import ProblemSets

class DetailsOfProblemSets (Base) :
    
    __tablename__ ="DetailsOfProblemSets"
    
    problemSetIndex =Column (INTEGER (unsigned =True), ForeignKey (ProblemSets.problemSetIndex, onupdate="CASCADE", ondelete="CASCADE"), primary_key =True, autoincrement =False, nullable =False)
    problemId =Column (INTEGER (unsigned =True), ForeignKey (Problems.problemId, onupdate="CASCADE", ondelete="CASCADE"), primary_key =True, autoincrement =False, nullable =False)