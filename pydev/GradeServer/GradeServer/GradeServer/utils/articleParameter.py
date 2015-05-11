# -*- coding: utf-8 -*-
"""
    GradeServer.utils
    ~~~~~~~~~~~~~~

    GradeSever에 적용될 ArticleParameter 대한 패키지 초기화 모듈.

    :copyright: (c) 2015 kookminUniv
    :@author: algolab
"""
    
class ArticleParameter:
    # filterCondition
    articleIndex = None
    boardLikerId = None
    
    def __init__(self, articleIndex = None, boardLikerId = None):
        self.articleIndex = articleIndex
        self.boardLikerId = boardLikerId