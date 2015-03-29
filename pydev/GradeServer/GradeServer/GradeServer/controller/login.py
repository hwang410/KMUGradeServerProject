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
from GradeServer.utils.utilQuery import select_accept_courses, select_notices, select_match_member, select_top_coder
from GradeServer.utils.utils import *

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
                    check = dao.query(select_match_member(memberId)).first ()
                    #Checking Success
                    if check.password == password:#check_password_hash (password, check.password)
                        flash(get_message('login'))
                        #push Session Cache 
                        session[MEMBER_ID] = memberId
                        session[AUTHORITY] = list(check.authority)
                        session[LAST_ACCESS_DATE] = datetime.now()
                        
                        ownCourses = select_accept_courses()
                        # Get My Accept Courses
                        try:
                            session[OWN_CURRENT_COURSES] = dao.query(ownCourses).\
                                                               filter(ownCourses.c.endDateOfCourse >= datetime.now()).\
                                                               all ()
                        except Exception:
                            session[OWN_CURRENT_COURSES] = []
                        
                        for k in session[OWN_CURRENT_COURSES]:
                            print k.courseId, k.courseName, k.endDateOfCourse
                            
                        try:
                            session[OWN_PAST_COURSES] = dao.query(ownCourses).\
                                                            filter(ownCourses.c.endDateOfCourse < datetime.now()).\
                                                            all ()
                        except Exception:
                            session[OWN_PAST_COURSES] = []
                        
                        for k in session[OWN_PAST_COURSES]:
                            print k.courseId, k.courseName, k.endDateOfCourse
                            
                                    
                        dao.query(Members).\
                            filter(Members.memberId == memberId).\
                            update(dict(lastAccessDate = session[LAST_ACCESS_DATE]))
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
   
    return render_template(MAIN_HTML,
                           notices = select_notices(),
                           topCoderId = select_top_coder(),
                           error = error)

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
    return redirect(url_for(SIGN_IN))