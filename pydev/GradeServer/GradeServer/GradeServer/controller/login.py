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
from flask import request, redirect, session, url_for, render_template, flash, make_response
from datetime import datetime

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer


@GradeServer.teardown_request
def close_db_session(exception = None):
    """요청이 완료된 후에 db연결에 사용된 세션을 종료함"""
    try:
        dao.remove()
    except Exception as e:
        from GradeServer.GradeServer_logger import Log
        Log.error(str(e))


"""
메인 페이지 및 로그인 관리 
"""
@GradeServer.route('/', methods = ['GET', 'POST'])
def sign_in():
    '''
    @@ Success sign in flash
    
    When the page redirected from sign up page,
    It display flash message.    
    '''
    if '?' in request.url:
        flash('Signed up successfully')
        
    """ main page before sign in"""
    from GradeServer.utils.utilMessages import get_message
    
    from GradeServer.utils.memberCourseProblemParameter import MemberCourseProblemParameter
    
    from GradeServer.utils.utilArticleQuery import select_notices
    from GradeServer.utils.utilQuery import select_accept_courses, select_past_courses, select_current_courses, select_match_member
    from GradeServer.utils.utilRankQuery import select_top_coder
    
    from GradeServer.resource.setResources import SETResources
    from GradeServer.resource.htmlResources import HTMLResources
    from GradeServer.resource.sessionResources import SessionResources
    from GradeServer.resource.languageResources import LanguageResources

    error = None
    if request.method == 'POST':
        checker = True
        for form in request.form:
            if "language" in form:
                checker = False
                resp = make_response(render_template(HTMLResources().const.MAIN_HTML,
                                                     SETResources = SETResources,
                                                     SessionResources = SessionResources,
                                                     LanguageResources = LanguageResources,
                                                     noticeRecords = select_notices(), 
                                                     topCoderId = select_top_coder(),
                                                     error = error))
                resp.set_cookie('language', request.form['language'])
                session['language'] = request.form['language']
                
        if checker:        
            if not request.form['memberId']:
                error = '아이디'  + get_message('fillData')
            elif not request.form['password']:
                error = '암호'  + get_message('fillData')
            else:
                try:
                    """ DB Password check """
                    memberId = request.form['memberId']
                    password = request.form['password']
                    
                    check = select_match_member(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = memberId)).first()
                    
                    from werkzeug.security import check_password_hash
                    
                    from GradeServer.resource.otherResources import OtherResources
                    from GradeServer.py3Des.pyDes import *
                    
                    tripleDes = triple_des(OtherResources().const.TRIPLE_DES_KEY,
                                           mode = ECB,
                                           IV = "\0\0\0\0\0\0\0\0",
                                           pad = None,
                                           padmode = PAD_PKCS5)
                    #Checking Success
                    if check_password_hash (check.password,
                                            tripleDes.encrypt(str(password))):
                        flash(get_message('login'))
                        #push Session Cache 
                        session[SessionResources().const.MEMBER_ID] = memberId
                        session[SessionResources().const.AUTHORITY] = list(check.authority)
                        session[SessionResources().const.LAST_ACCESS_DATE] = datetime.now()
                        
                        # set default language
                        session['language'] = 'en'
                                                    
                        ownCourses = select_accept_courses().subquery()
                        # Get My Accept Courses
                        try:
                            session[SessionResources().const.OWN_CURRENT_COURSES] = select_current_courses(ownCourses).all()
                        except Exception:
                            session[SessionResources().const.OWN_CURRENT_COURSES] = []
                        try:
                            session[SessionResources().const.OWN_PAST_COURSES] = select_past_courses(ownCourses).all()
                        except Exception:
                            session[SessionResources().const.OWN_PAST_COURSES] = []
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
            
    return render_template(HTMLResources().const.MAIN_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           LanguageResources = LanguageResources,
                           noticeRecords = select_notices(),
                           topCoderId = select_top_coder(),
                           error = error)
               
               
''' 
Update Login Time
'''
def update_recent_access_date(memberId):
    from GradeServer.model.members import Members
    
    dao.query(Members).\
        filter(Members.memberId == memberId).\
        update(dict(lastAccessDate = datetime.now()))
        
        
"""
로그아웃
"""
from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.checkInvalidAccess import check_invalid_access
@GradeServer.route ('/signout')
@check_invalid_access
@login_required
def sign_out():
    """ Log Out """ 
    # 세션 클리어
    session.clear()
    # 메인 페이지로 옮기기
    from GradeServer.resource.routeResources import RouteResources
    return redirect(url_for(RouteResources().const.SIGN_IN))
