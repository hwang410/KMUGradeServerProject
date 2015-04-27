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
from datetime import datetime
from werkzeug.security import check_password_hash

from GradeServer.utils.utilMessages import get_message
from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilQuery import select_accept_courses, select_past_courses, select_current_courses, select_notices, select_match_member
from GradeServer.utils.utilRankQuery import select_top_coder

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.model.members import Members
from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer


@GradeServer.teardown_request
def close_db_session(exception = None):
    """요청이 완료된 후에 db연결에 사용된 세션을 종료함"""
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))
        
"""
메인 페이지 및 로그인 관리 
"""
@GradeServer.route('/', methods = ['GET', 'POST'])
def sign_in():
    """ main page before sign in"""
    error = None
    
    if request.method == 'POST':
        if not request.form['memberId']:
            error = '아이디'  + get_message('fillData')
        elif not request.form['password']:
            error = '암호'  + get_message('fillData')
        else:
            try:
                """ DB Password check """
                memberId = request.form['memberId']
                password = request.form['password']
                
                try :
                    check = select_match_member(memberId).first()
                    #Checking Success
                    if check.password == password:#check_password_hash (password, check.password)
                        flash(get_message('login'))
                        #push Session Cache 
                        session[SessionResources.const.MEMBER_ID] = memberId
                        session[SessionResources.const.AUTHORITY] = list(check.authority)
                        session[SessionResources.const.LAST_ACCESS_DATE] = datetime.now()
                        ownCourses = select_accept_courses().subquery()
                        # Get My Accept Courses
                        try:
                            session[SessionResources.const.OWN_CURRENT_COURSES] = select_current_courses(ownCourses).all()
                        except Exception:
                            session[SessionResources.const.OWN_CURRENT_COURSES] = []
                        try:
                            session[SessionResources.const.OWN_PAST_COURSES] = select_past_courses(ownCourses).all()
                            print "CCCCCCCCCCCCCCCCL", len(session[SessionResources.const.OWN_PAST_COURSES])
                        except Exception:
                            print "AAAAAAAZZZ"
                            session[SessionResources.const.OWN_PAST_COURSES] = []
                        update_recent_access_date(memberId)
                        # Commit Exception
                        try:
                            dao.commit()
                        except Exception:
                            dao.rollback()
                            error = get_message('updateFailed')
                    else:
                        error = get_message('tryAgain')
                # Not Exist MemberId
                except Exception:
                    error = get_message('notExists')

            except Exception as e:
                Log.error(str(e))
            
    
    return render_template(HTMLResources.const.MAIN_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           noticeRecords = select_notices(),
                           topCoderId = select_top_coder(),
                           error = error)
               
               
''' 
Update Login Time
'''
def update_recent_access_date(memberId):
    dao.query(Members).\
        filter(Members.memberId == memberId).\
        update(dict(lastAccessDate = datetime.now()))
        
        
"""
로그아웃
"""
@GradeServer.route ('/signout')
@login_required
def sign_out():
    """ Log Out """ 
    # 세션 클리어
    session.clear()
    # 메인 페이지로 옮기기
    return redirect(url_for(RouteResources.const.SIGN_IN))
