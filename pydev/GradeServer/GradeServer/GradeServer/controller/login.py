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
from flask import request, redirect, session, url_for, render_template, flash
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from operator import attrgetter

from GradeServer.model.members import Members
from GradeServer.model.registrations import Registrations
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.submissions import Submissions
from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils import login_required, get_rank, get_message

from GradeServer.model.submittedFiles import SubmittedFiles

@GradeServer.teardown_request
def close_db_session(exception=None):
    """요청이 완료된 후에 db연결에 사용된 세션을 종료함"""
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))
        
"""
메인 페이지 및 로그인 관리 
"""
@GradeServer.route('/', methods=['GET', 'POST'])
def sign_in(error =None):
    """ main page before sign in"""

    if request.method == 'POST':
        if not request.form['memberId']:
            error =get_message ('fillMemberId')
        elif not request.form['password']:
            error =get_message ('fillPassword')
        else:
            try :
                """ DB Password check """
                memberId = request.form['memberId']
                password =request.form['password']
                
                check =dao.query (Members).filter_by (memberId =memberId).first ()
                #Checking Success
                if check.password == password :#check_password_hash (password, check.password)
                    flash ("Login!!")
                    #push Session Cache 
                    session['memberId'] =memberId
                    session['authority'] = list(check.authority)
                    session['lastAccessDate'] =datetime.now()
                    
                    for authority in session['authority']:
                        if authority == "ServerAdministrator":
                            session['ownCourses'] = dao.query(RegisteredCourses).all()
                        elif authority == "CourseAdministrator":
                            session['ownCourses'] = dao.query(RegisteredCourses).filter_by(courseAdministratorId=session['memberId']).all()   
                        else:
                            session['ownCourses'] = dao.query(RegisteredCourses.courseId, RegisteredCourses.courseName, Registrations.memberId).\
                                                    join(Registrations, RegisteredCourses.courseId == Registrations.courseId).\
                                                    filter(Registrations.memberId == session['memberId']).all()
                                    
                            
                    dao.query(Members).filter_by(memberId=session['memberId']).update(dict(lastAccessDate=session['lastAccessDate']))
                    # Commit Exception
                    try :
                        dao.commit()
                    except Exception :
                        dao.rollback ()
                        error =get_message ('updateFailed')
                else :
                    error =get_message ('tryAgain')

            except Exception as e :
                Log.error (str(e))
    
    return render_template('/main.html', notices=get_notices(), topCoderId =get_top_coder (), error=error)

"""
로그아웃
"""
@GradeServer.route ('/signout')
@login_required
def sign_out () :
    """ Log Out """ 
    # 세션 클리어
    session.clear ()
    # 메인 페이지로 옮기기
    return redirect (url_for ('.sign_in'))


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