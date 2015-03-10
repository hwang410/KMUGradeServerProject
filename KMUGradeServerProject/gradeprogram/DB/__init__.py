# -*- coding: utf-8 -*-
"""
    GradeServer.model
    ~~~~~~~~~~~~~~

    GradeSever에 적용될 model에 대한 패키지 초기화 모듈.

    :copyright: (c) 2015 kookminUniv
"""


from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

__all__ = ['member', 'language', 'course', 'problem', 'submit', 'problemType', 'department']