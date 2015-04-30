# -*- coding: utf-8 -*-

from flask import request, render_template, url_for, redirect, session, flash

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.utilQuery import select_count, select_solved_problem_count, select_submission_count,\
                                        select_solved_count, select_wrong_answer_count, select_time_over_count,\
                                        select_compile_error_count, select_runtime_error_count, select_server_error_count
from GradeServer.utils.utilSubmissionQuery import submissions_sorted, select_all_submission

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao

from GradeServer.model.problems import Problems
from GradeServer.model.members import Members
from GradeServer.model.submissions import Submissions
from GradeServer.model.departments import Departments
from GradeServer.model.languages import Languages
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.colleges import Colleges

from GradeServer.controller.serverMaster import *
from GradeServer.controller.classMaster import *

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
로그인한 유저가 제출 했던 모든기록
"""
@GradeServer.route('/user_history/<memberId>-<sortCondition>/page<pageNum>')
@login_required
def user_history(memberId, sortCondition, pageNum):
    try:       
        # 모든 제출 정보
        submissions = select_all_submission(lastSubmission = None,
                                            memberId = memberId).subquery()
        
        # List Count
        try:
            count = select_count(submissions.c.memberId).first().\
                                                         count  
        except Exception:
            count = 0
         
        try:
                        # 차트 정보
            chartSubmissionRecords = dao.query(# 중복 제거푼 문제숫
                                               select_solved_problem_count(submissions).subquery(),
                                                                                              # 총 제출 횟수
                                               select_submission_count(submissions).subquery(),
                                                                                              # 모든 맞춘 횟수
                                               select_solved_count(submissions).subquery(),
                                                                                              # 틀린 횟수
                                               select_wrong_answer_count(submissions).subquery(),
                                                                                              # 타임 오버 횟수
                                               select_time_over_count(submissions).subquery(),
                                                                                              # 컴파일 에러 횟수
                                               select_compile_error_count(submissions).subquery(),
                                                                                              # 런타임 에러 횟수
                                               select_runtime_error_count(submissions).subquery(),
                                                                                              # 서버 에러 횟수
                                               select_server_error_count(submissions).subquery()).\
                                         first()
        except Exception:
            #None Type Exception
            chartSubmissionRecords = []
        # Viiew Value Text
        chartSubmissionDescriptions = ['맞춘 문제 갯수','총 제출 횟수', '맞춘 횟수', '오답 횟수', '타임오버 횟수', '컴파일 에러 횟수', '런타임 에러 횟수', '서버 에러 횟수']
        
        try:                           
                        # 모든 제출 정보
            # Sorted
            submissionRecords = get_page_record(submissions_sorted(submissions,
                                                                   sortCondition = sortCondition),
                                                pageNum = int(pageNum)).all()
        except Exception:
            #None Type Exception
            submissionRecords = []
       
        return render_template(HTMLResources().const.SUBMISSION_RECORD_HTML,
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               memberId = memberId,
                               sortCondition = sortCondition,
                               submissionRecords = submissionRecords,
                               chartSubmissionDescriptions = chartSubmissionDescriptions,
                               chartSubmissionRecords = chartSubmissionRecords,
                               pages = get_page_pointed(pageNum = int(pageNum),
                                                        count = count))
    except Exception:
        # Unknow Error
        return unknown_error()

"""
로그인한 유저가 권한이 필요한 페이지에 접급하기전
본인인지 확인하기 위한 페이지
"""
@GradeServer.route('/id_check/<select>', methods = ['GET', 'POST'])
@login_required
def id_check(select, error = None):
    if request.method == 'POST':
        # 암호를 입력 안했을 때
        if not request.form['password']:
            error ='Password' + get_message('fillData')
        else:
            try:
                memberId = session[SessionResources().const.MEMBER_ID]
                password = request.form['password']
                check = dao.query(Members.password).\
                            filter(Members.memberId == memberId).first()
                
                # 암호가 일치 할 때
                if check.password == password:#check_password_hash(password, check.password):
                    # for all user
                    if select == 'account':
                        return redirect(url_for(RouteResources().const.EDIT_PERSONAL))
                    # server manager
                    elif SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY][0]:
                        if select == 'server_manage_collegedepartment':
                            return redirect(url_for('.server_manage_collegedepartment'))
                        elif select == 'server_manage_class':
                            print "ABBB"
                            return redirect(url_for('.server_manage_class'))
                        elif select == 'server_manage_problem':
                            return redirect(url_for('.server_manage_problem'))
                        elif select == 'server_manage_user':
                            return redirect(url_for('.server_manage_user'))
                        elif select == 'server_manage_service':
                            return redirect(url_for('.server_manage_service'))
                    # class manager
                    elif SETResources().const.COURSE_ADMINISTRATOR in session[SessionResources().const.AUTHORITY][0]:
                        if select == 'user_submit':
                            return redirect(url_for('.class_user_submit'))
                        elif select == 'cm_manage_problem':
                            return redirect(url_for('.class_manage_problem'))
                        elif select == 'cm_manage_user':
                            return redirect(url_for('.class_manage_user'))
                        elif select == 'cm_manage_service':
                            return redirect(url_for('.class_manage_service'))
                    else:
                        return unknown_error()
                # 암호가 일치 하지 않을 때
                else:
                    error = get_message('wrongPassword')
            except Exception as e:
                Log.error(str(e))
                raise e
               
    return render_template(HTMLResources().const.ID_CHECK_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           error = error)

"""
로그인한 유저가 자신의 암호, 연락처 등을 바꿀수 있고
자신의 장보를 확인 할 수 있는 페이지
"""
# ContactNumber, E-mail, comment 저장할 전역 변수
gContactNumber, gEmailAddress, gComment = None, None, None
@GradeServer.route('/edit_personal', methods = ['GET', 'POST'])
@login_required
def edit_personal(error = None):
    try:
        global gContactNumber, gEmailAddress, gComment
        #Get User Information
        try:
            memberInformation = dao.query(Members.memberId,
                                          Members.memberName,
                                          Members.contactNumber,
                                          Members.emailAddress,
                                          Members.comment,
                                          Colleges.collegeName,
                                          Departments.departmentName).\
                                    filter(Members.memberId == session[SessionResources().const.MEMBER_ID]).\
                                    outerjoin(DepartmentsDetailsOfMembers,
                                         Members.memberId == DepartmentsDetailsOfMembers.memberId).\
                                    outerjoin(Colleges,
                                         Colleges.collegeIndex == DepartmentsDetailsOfMembers.collegeIndex).\
                                    outerjoin(Departments,
                                         Departments.departmentIndex == DepartmentsDetailsOfMembers.departmentIndex).\
                                    first()
        except Exception:
            #None Type Exception
            memberInformation = []
        
        
        #Get Post
        if request.method == 'POST':
            
            password = request.form['password']
            passwordConfirm = request.form['passwordConfirm'] 
            #Get Updating Data
            gContactNumber = request.form['contactNumber'] if gContactNumber != request.form['contactNumber'] else gContactNumber
            memberInformation.contactNumber = gContactNumber
            gEmailAddress = request.form['emailAddress'] if gEmailAddress != request.form['emailAddress'] else gEmailAddress
            memberInformation.emailAddress = gEmailAddress
            gComment = request.form['comment'] if gComment != request.form['comment'] else gComment
            memberInformation.comment = gComment
            #Password Same
            if(password and passwordConfirm) and password == passwordConfirm:
                #Generate Password
                #password =generate_password_hash(password)
                passwordConfirm = None
                
                #Update DB
                dao.query(Members).\
                    filter(Members.memberId == session[SessionResources().const.MEMBER_ID]).\
                    update(dict(password = password,
                                contactNumber = gContactNumber,
                                emailAddress = gEmailAddress,
                                comment = gComment))
                # Commit Exception
                try:
                    # global Value Init
                    gContactNumber, gEmailAddress, gComment = None, None, None
                    
                    dao.commit()
                    flash(get_message('updateSucceeded'))
                    
                    return redirect(url_for(RouteResources().const.SIGN_IN))
                except Exception:
                    dao.rollback()
                    error = get_message('upateFailed')
                
            #Password Different
            elif not password or not passwordConfirm:
                error = 'Confirm Password' + get_message('fillData')
            else:
                error = get_message('wrongPassword')
        
        return render_template(HTMLResources().const.EDIT_PERSONAL_HTML,
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               memberInformation = memberInformation,
                               gContactNumber = gContactNumber,
                               gEmailAddress = gEmailAddress,
                               gComment = gComment,
                               error = error)
    except Exception:
        gContactNumber, gEmailAddress, gComment = None, None, None
        
        return unknown_error()
    
""" ===== end Basic user space ===== """


""" ===== class master space ===== """

""" ===== end class master space ===== """

""" ===== server master space ===== """

""" ===== end server master space ===== """