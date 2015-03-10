# -*- coding: utf-8 -*-
"""
    GradeSever.controller.login
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    로그인 확인 데코레이터와 로그인 처리 모듈.

    :copyright: (c) 2015 by KookminUniv

"""

"""
bug reporting

if path is a/b/c/d, it can't recognize any .css and .js file.
(a/b/c is okay)
"""

import math

from flask import request, redirect, session, url_for, current_app
from functools import wraps
from sqlalchemy import func

from GradeServer.model.members import Members
from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log


def login_required(f):
    """현재 사용자가 로그인 상태인지 확인하는 데코레이터
    로그인 상태에서 접근 가능한 함수에 적용함
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session_key = \
                request.cookies.get(
                    current_app.config['SESSION_COOKIE_NAME'])

            if not (session.sid == session_key and session.__contains__('memberId')) :
                session.clear()
                
                return redirect(url_for('.sign_in'))
            
            return f(*args, **kwargs)

        except Exception as e:
            Log.error("GradeServer Login Required Error : %s" % str(e))
            raise e

    return decorated_function

"""
페이징에 필요한 정보들을 구하는 모듈
"""
def get_page_pointed (pageNum, count, BLOCK =6, LIST =15) :
    
    #Show List
    startList =(pageNum -1) *LIST
    endList =(pageNum *LIST) if startList +LIST < count -1 else count
    #show Page
    block =(pageNum -1) /BLOCK
    startPage =block +1
    endPage =block +BLOCK 
    allPage =int(math.ceil (count /LIST))
    #Minimum Page
    if endPage > allPage :
        endPage =allPage
    page_dick ={'BLOCK' :BLOCK, 'pageNum' :pageNum, 'startList' :startList, 'endList' :endList, 'startPage' :startPage, 'endPage' :endPage, 'allPage' :allPage}
    
    return page_dick


"""
기본 랭크 
"""
def get_rank (submissions) :
    #Get SubmitCount
    submissionCount =dao.query (submissions.c.memberId, func.sum (submissions.c.solutionCheckCount).label ("submissionCount")).\
        group_by (submissions.c.memberId).subquery ()
    #Get Solved Count
    status =dao.query (submissions.c.memberId, func.count (submissions.c.status).label ("solvedCount")).filter (submissions.c.status == 'Solved').\
        group_by (submissions.c.memberId).subquery ()
    #SubmitCount and SolvedCount Join
    submissions =dao.query (submissionCount.c.memberId, submissionCount.c.submissionCount, status.c.solvedCount,
                            (status.c.solvedCount /submissionCount.c.submissionCount *100).label ("solvedRate")).\
        join (status, submissionCount.c.memberId == status.c.memberId).subquery ()
    
    try :
        #Get Comment
        rankMemberRecords =dao.query (Members.memberId, Members.comment, submissions.c.submissionCount, submissions.c.solvedCount, submissions.c.solvedRate).\
            join (submissions, Members.memberId == submissions.c.memberId).\
            order_by (submissions.c.solvedRate.desc ()).all ()
    except Exception :
        # None Type Exception
        rankMemberRecords =[]
        
    return rankMemberRecords