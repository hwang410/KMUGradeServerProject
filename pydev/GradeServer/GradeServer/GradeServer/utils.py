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

from flask import request, redirect, session, url_for, current_app, render_template
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
나쁜 말 & 좋은 말 메세지 모음
"""
def get_message (key ="unknown") :
    messageDict ={"unknown" :"죄송 합니다. 알수 없는 에러 입니다.",
                  "tryAgain" :"다시 시도해 주시기 바랍니다.",
                  "accessFailed" :"접근 할 수 있는 권한이 없습니다.",
                  "updateFailed" :"정보 갱신에 실패하였습니다.",
                  "updateSuccessed" :"정보 갱신에 성공 하였습니다!!!",
                  "notExists" :"해당 아이디가 없습니다.",
                  "alreadyExists" :"이미 있는 아이디 입니다.",
                  "fillMemberId" :"아이디를 입력해 주시기 바랍니다.",
                  "fillPassword" :"암호를 입력해 주시기 바랍니다.",
                  "fillConfirmPassword" :"확인 암호를 입력해 주시기 바랍니다.",
                  "wrongPassword" :"암호가 일치하지 않습니다.",
                  "acceptInvitee" :"팀에 합류 되었습니다!!!",
                  "rejectInvitee" :"팀 초대를 거절 하셨습니다!!!",
                  "notSelf" :"자기 자신을 설정 할 수 없습니다.",
                  "notTeamMemberInvitee" :"팀 원을 초대 할 수 없습니다.",
                  "inviteeSuccessed" :"님을 초대 하였습니다!!!",
                  "fillTeamName" :"팀 명을 입력해 주세요.",
                  "existTeamName" :"같은 팀 명이 존재 합니다.",
                  "makeTeamSuccessed" :"팀이 만들어졌습니다!!!",
                  "removeTeamSuccessed" :"팀이 삭제 되었습니다!!!"}

    return messageDict[key]


"""
오류로 인한  메인  페이지 이동
"""
def unknown_error (error =get_message ()) :
    return redirect (url_for ('.sign_in', error =error))# render_template('/main.html', error =error)

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
def get_rank (submissions, sortCondition ="rate") :
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
        # rate 정렬
        if sortCondition == "rate" :
            rankMemberRecords =dao.query (Members.memberId, Members.comment, submissions.c.submissionCount, submissions.c.solvedCount, submissions.c.solvedRate).\
                join (submissions, Members.memberId == submissions.c.memberId).\
                order_by (submissions.c.solvedRate.desc ()).all ()
        else : #if sortCondition == "problem"
            rankMemberRecords =dao.query (Members.memberId, Members.comment, submissions.c.submissionCount, submissions.c.solvedCount, submissions.c.solvedRate).\
                join (submissions, Members.memberId == submissions.c.memberId).\
                order_by (submissions.c.solvedCount.desc ()).all ()
    except Exception :
        # None Type Exception
        rankMemberRecords =[]
        
    return rankMemberRecords