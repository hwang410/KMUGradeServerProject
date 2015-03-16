 # -*- coding: utf-8 -*-
"""
    GradeSever.uilts
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    공용 처리 모듈.

    :copyright: (c) 2015 by KookminUniv

"""

"""
bug reporting

if path is a/b/c/d, it can't recognize any .css and .js file.
(a/b/c is okay)
"""

import math

from flask import request, redirect, session, current_app, render_template
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from operator import attrgetter

from GradeServer.model.members import Members
from GradeServer.model.registrations import Registrations
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.submissions import Submissions
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
                  "wrongPassword" :"암호가 일치하지 않습니다.",
                  "fillData" :"를(을) 입력해 주시기 바랍니다.",
                  
                  "writtenComment" :"댓글을 작성 하였습니다!!!",
                  "deletedComment" :"댓글을 삭제 하였습니다!!!",
                  "writtenPost" :"게시물을 작성 하였습니다!!!",
                  "modifiedPost" :"게시물을 수정 하였습니다!!!",
                  "deletedPost" :"게시물을 삭제 하였습니다!!!",
                  
                  "acceptInvitee" :"팀에 합류 되었습니다!!!",
                  "rejectInvitee" :"팀 초대를 거절 하셨습니다!!!",
                  "notSelf" :"자기 자신을 설정 할 수 없습니다.",
                  "notTeamMemberInvitee" :"팀 원을 초대 할 수 없습니다.",
                  "inviteeSuccessed" :"님을 초대 하였습니다!!!",
                  "existTeamName" :"같은 팀 명이 존재 합니다.",
                  "makeTeamSuccessed" :"팀이 만들어졌습니다!!!",
                  "removeTeamSuccessed" :"팀이 삭제 되었습니다!!!"}

    return messageDict[key]


"""
오류로 인한  메인  페이지 이동
"""
def unknown_error (error =get_message ()) :
    return render_template('/main.html', notices=get_notices(), topCoderId =get_top_coder (), error=error)

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


"""
권한 별로 공지 가져오기
"""
def get_notices () :
    # Notices Layer
    try :
        # 서버 공지만
        try :
            serverAdministratorId =dao.query (Members.memberId).filter_by (authority ='ServerAdministrator').first ().memberId
            serverAdministratorNotices =dao.query (ArticlesOnBoard).\
                filter_by (isNotice ='Notice', writerId =serverAdministratorId).subquery ()
            serverAdministratorNotices =dao.query (serverAdministratorNotices, RegisteredCourses.courseName).\
                join (RegisteredCourses, serverAdministratorNotices.c.courseId == RegisteredCourses.courseId).all ()
        except Exception :
            serverAdministratorNotices =[]
            
        # 로그인 상태
        try :
            if login_required :
                # 서버 관리자는 모든 공지
                if "ServerAdministrator" in session['authority'] :
                    notices =dao.query (ArticlesOnBoard).filter_by (isNotice ='Notice').all ()
                # 과목 관리자 및 유저는 담당 과목 공지
                else :
                    if "CourseAdministrator" in session['authority'] :
                        registeredCourseId =dao.query (RegisteredCourses.courseId).\
                            filter_by (courseAdministratorId =session['memberId']).subquery ()
                    else :
                        registeredCourseId =dao.query (Registrations.courseId).filter_by (memberId =session['memberId']).subquery ()
                    notices =dao.query (ArticlesOnBoard).\
                            join (registeredCourseId, ArticlesOnBoard.courseId == registeredCourseId.c. courseId).\
                            filter (ArticlesOnBoard.isNotice == 'Notice').subquery ()
                    notices =dao.query (notices, RegisteredCourses.courseName).\
                        join (RegisteredCourses, notices.c.courseId == RegisteredCourses.courseId).all ()
                    notices.extend(serverAdministratorNotices)
                    
        except Exception :
            # Not Login
            notices =serverAdministratorNotices

        # articleIndex 정렬
        notices =sorted (notices, key =attrgetter ('writtenDate'), reverse =True)
        # 최대 5개만 보여주므로 그 밑에는 자르기
        if len (notices) > 5 :
            notices =notices[:5]   
    except Exception :
        # query get All Error None type Error
        notices =[]
    
    return notices 
    
"""
Top Coder
"""
def get_top_coder () :
     # Top Coder Layer
    try :
        # 오늘 요일 월1 ~ 일7
        dayOfWeek =datetime.now ().isoweekday ()
        # 요일 별 제출 기간 추려내기
        dayOfWeekMap ={7 :sunday,
                       1 :monday,
                       2 :tuesday,
                       3 :wednesday,
                       4 :thursday,
                       5 :friday,
                       6 :saturday}
        # 금주의 시작일과 끝일 구함
        submissionDatePeriod =dayOfWeekMap[dayOfWeek] (dateFormat ="%Y-%m-%d")
        # 이번주에 낸 제출 목록 
        dayOfWeekSubmissions =dao.query (Submissions.memberId, Submissions.solutionCheckCount, Submissions.status).\
            filter (Submissions.codeSubmissionDate.between (submissionDatePeriod['start'], submissionDatePeriod['end'])).\
            group_by (Submissions.memberId, Submissions.problemId, Submissions.courseId).subquery ()

        topCoder =get_rank (dayOfWeekSubmissions)
        if topCoder :
            topCoderId =topCoder[0].memberId
        else :
            topCoderId =None
    except Exception :
        # None Type Error
        topCoderId =get_message ('unknown')
        
    return topCoderId

# 요일 별로 금주 기간 지정
def sunday (dateFormat ="%Y-%m-%d", minusDays =-0, addDays =6) :
    # 현재 날짜에서 6일후 날짜까지 구함
    # 현재 날짜에서 -0, +6
    startDate =(datetime.now () +timedelta (days =minusDays)).strftime (dateFormat)
    endDate =(datetime.now () +timedelta (days =addDays)).strftime(dateFormat) 
    submissionDatePeriod ={'start' :startDate, 'end' :endDate}
    
    return submissionDatePeriod

def monday (dateFormat ="%Y-%m-%d", minusDays =-1, addDays =5) :
    # 어제 날짜에서 5일후 날짜까지 구함
    # 현재 날짜에서 -1, +5
    startDate =(datetime.now () +timedelta (days =minusDays)).strftime (dateFormat)
    endDate =(datetime.now () +timedelta (days =addDays)).strftime(dateFormat) 
    submissionDatePeriod ={'start' :startDate, 'end' :endDate}
    
    return submissionDatePeriod

def tuesday (dateFormat ="%Y-%m-%d", minusDays =-2, addDays =4) :
    # 그저게 날짜에서 4일후 날짜까지 구함
    # 현재 날짜에서 -2, +4
    startDate =(datetime.now () +timedelta (days =minusDays)).strftime (dateFormat)
    endDate =(datetime.now () +timedelta (days =addDays)).strftime(dateFormat) 
    submissionDatePeriod ={'start' :startDate, 'end' :endDate}
    
    return submissionDatePeriod

def wednesday (dateFormat ="%Y-%m-%d", minusDays =-3, addDays =3) :
    # 3일전 날짜에서 3일후 날짜까지 구함
    # 현재 날짜에서 -3, +3
    startDate =(datetime.now () +timedelta (days =minusDays)).strftime (dateFormat)
    endDate =(datetime.now () +timedelta (days =addDays)).strftime(dateFormat) 
    submissionDatePeriod ={'start' :startDate, 'end' :endDate}
    
    return submissionDatePeriod

def thursday (dateFormat ="%Y-%m-%d", minusDays =-4, addDays =2) :
    # 4일전 날짜에서 2일 후 날짜까지 구함
    # 현재 날짜에서 -4, +2
    startDate =(datetime.now () +timedelta (days =minusDays)).strftime (dateFormat)
    endDate =(datetime.now () +timedelta (days =addDays)).strftime(dateFormat) 
    submissionDatePeriod ={'start' :startDate, 'end' :endDate}
    
    return submissionDatePeriod

def friday (dateFormat ="%Y-%m-%d", minusDays =-5, addDays =1) :
    # 5일전 날짜에서 1일후 날짜까지 구함
    # 현재 날짜에서 -5, +1
    startDate =(datetime.now () +timedelta (days =minusDays)).strftime (dateFormat)
    endDate =(datetime.now () +timedelta (days =addDays)).strftime(dateFormat) 
    submissionDatePeriod ={'start' :startDate, 'end' :endDate}
    
    return submissionDatePeriod

def saturday (dateFormat ="%Y-%m-%d", minusDays =-6, addDays =0) :
    # 6일전 날짜에서 오늘 날짜까지 구함
    # 현재 날짜에서 -6, +0
    startDate =(datetime.now () +timedelta (days =minusDays)).strftime (dateFormat)
    endDate =(datetime.now () +timedelta (days =addDays)).strftime(dateFormat) 
    submissionDatePeriod ={'start' :startDate, 'end' :endDate}
    
    return submissionDatePeriod