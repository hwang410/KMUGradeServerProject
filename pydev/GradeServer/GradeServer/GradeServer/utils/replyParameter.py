# -*- coding: utf-8 -*-
"""
    GradeServer.utils
    ~~~~~~~~~~~~~~

    GradeSever에 적용될 ReplyParameter 대한 패키지 초기화 모듈.

    :copyright: (c) 2015 kookminUniv
    :@author: algolab
"""
    
class ReplyParameter:
    # filterCondition
    boardReplyIndex = None
    boardReplyLikerId = None
    boardReplyContent = None
    
    
    def __init__(self, boardReplyIndex = None, boardReplyLikerId = None, boardReplyContent = None):
        self.boardReplyIndex = boardReplyIndex
        self.boardReplyLikerId = boardReplyLikerId
        self.boardReplyContent = boardReplyContent