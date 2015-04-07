# -*- coding: utf-8 -*-

import math 

from GradeServer.utils.utils import BLOCK, LIST

"""
페이징에 필요한 정보들을 구하는 모듈
"""
def get_page_pointed(pageNum, count, BLOCK = BLOCK, LIST = LIST):
    
    #Show List
    startList = (pageNum - 1) * LIST
    endList = (pageNum * LIST) if startList + LIST < count - 1 else count
    #show Page
    block = pageNum / BLOCK if pageNum < BLOCK else pageNum - BLOCK
    startPage = block + 1 
    endPage = block + BLOCK 
    allPage = int(math.ceil(count / float(LIST)))
    #Minimum Page
    if endPage > allPage:
        endPage = allPage
        
    return {'LIST': LIST,
            'BLOCK': BLOCK,
            'pageNum': pageNum,
            'startList': startList,
            'endList': endList,
            'startPage': startPage,
            'endPage': endPage,
            'allPage': allPage}
    
    
'''
Page Number Case Record
'''
def get_page_record(recordsSub, pageNum, LIST = LIST):
        
    return recordsSub.slice((pageNum - 1) * LIST,
                            pageNum * LIST)
