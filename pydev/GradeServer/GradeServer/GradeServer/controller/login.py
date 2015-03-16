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

from GradeServer.model.members import Members
from GradeServer.model.registrations import Registrations
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils import login_required, get_rank, get_message, get_notices, get_top_coder

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
def sign_in():
    """ main page before sign in"""
    error =None
    
    if request.method == 'POST':
        if not request.form['memberId']:
            error ='아이디' +get_message ('fillData')
        elif not request.form['password']:
            error ='암호' +get_message ('fillData')
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