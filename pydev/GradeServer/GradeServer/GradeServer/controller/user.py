# -*- coding: utf-8 -*-

from flask import request, render_template, url_for, redirect, session, flash

from werkzeug.security import check_password_hash, generate_password_hash

from GradeServer.py3Des.pyDes import *

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.checkInvalidAccess import check_invalid_access

from GradeServer.utils.memberCourseProblemParameter import MemberCourseProblemParameter

from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.utilQuery import select_count, select_match_member
from GradeServer.utils.utilSubmissionQuery import submissions_sorted, select_all_submissions, select_member_chart_submissions
from GradeServer.utils.utilUserQuery import join_member_informations, update_member_informations

from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.languageResources import LanguageResources

from GradeServer.database import dao

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
@GradeServer.route('/submission_record/<memberId>-<sortCondition>/page<int:pageNum>')
@check_invalid_access
@login_required
def submission_record(memberId, sortCondition, pageNum):
    try:       
        # 모든 제출 정보
        submissions = select_all_submissions(lastSubmission = None,
                                             memberCourseProblemParameter = MemberCourseProblemParameter(memberId = memberId)).subquery()
        # List Count
        try:
            count = select_count(submissions.c.memberId).first().\
                                                         count  
        except Exception:
            count = 0
         
        try:
                        # 차트 정보
            chartSubmissionRecords = select_member_chart_submissions(submissions).first()
        except Exception:
            #None Type Exception
            chartSubmissionRecords = []
        # Viiew Value Text
        chartSubmissionDescriptions = ['Solved Problems',
                                       'Total Submissions',
                                       'Solved',
                                       'Wrong answer',
                                       'Timeover',
                                       'Compile error',
                                       'Runtime error',
                                       'Server error']
        
        try:                           
                        # 모든 제출 정보
            # Sorted
            submissionRecords = get_page_record(submissions_sorted(submissions,
                                                                   sortCondition = sortCondition),
                                                pageNum = pageNum).all()
        except Exception:
            #None Type Exception
            submissionRecords = []
            
        return render_template(HTMLResources().const.SUBMISSION_RECORD_HTML,
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               memberId = memberId,
                               sortCondition = sortCondition,
                               submissionRecords = submissionRecords,
                               chartSubmissionDescriptions = chartSubmissionDescriptions,
                               chartSubmissionRecords = chartSubmissionRecords,
                               pages = get_page_pointed(pageNum = pageNum,
                                                        count = count))
    except Exception:
        # Unknow Error
        return unknown_error()

"""
로그인한 유저가 권한이 필요한 페이지에 접급하기전
본인인지 확인하기 위한 페이지
"""
@GradeServer.route('/id_check/<select>', methods = ['GET', 'POST'])
@check_invalid_access
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
                check = select_match_member(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = memberId)).first()
                
                                # 암호가 일치 할 때
                tripleDes = triple_des(OtherResources().const.TRIPLE_DES_KEY,
                                       mode = ECB,
                                       IV = "\0\0\0\0\0\0\0\0",
                                       pad = None,
                                       padmode = PAD_PKCS5)
                #Checking Success
                if check_password_hash (check.password,
                                        tripleDes.encrypt(str(password))):
                    # for all user
                    if select == 'account':
                        return redirect(url_for(RouteResources().const.EDIT_PERSONAL))
                    # server manager
                    elif SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY][0]:
                        if select == 'server_manage_collegedepartment':
                            return redirect(url_for('.server_manage_collegedepartment'))
                        elif select == 'server_manage_class':
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
                           LanguageResources = LanguageResources,
                           error = error)

"""
로그인한 유저가 자신의 암호, 연락처 등을 바꿀수 있고
자신의 장보를 확인 할 수 있는 페이지
"""
# ContactNumber, E-mail, comment 저장할 전역 변수
gContactNumber, gEmailAddress, gComment = None, None, None
@GradeServer.route('/edit_personal', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def edit_personal(error = None):
    try:
        global gContactNumber, gEmailAddress, gComment
        #Get User Information
        try:
            memberInformation = join_member_informations(select_match_member(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = session[SessionResources().const.MEMBER_ID])).subquery()).first()
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
                tripleDes = triple_des(OtherResources().const.TRIPLE_DES_KEY,
                                       mode = ECB,
                                       IV = "\0\0\0\0\0\0\0\0",
                                       pad = None,
                                       padmode = PAD_PKCS5)
                
                password = generate_password_hash(tripleDes.encrypt(str(password)))
                passwordConfirm = None
                
                #Update DB
                update_member_informations(select_match_member(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = session[SessionResources().const.MEMBER_ID])),
                                           password,
                                           gContactNumber,
                                           gEmailAddress,
                                           gComment)
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
                               LanguageResources = LanguageResources,
                               memberInformation = memberInformation,
                               gContactNumber = gContactNumber,
                               gEmailAddress = gEmailAddress,
                               gComment = gComment,
                               error = error)
    except Exception:
        gContactNumber, gEmailAddress, gComment = None, None, None
        
        return unknown_error()