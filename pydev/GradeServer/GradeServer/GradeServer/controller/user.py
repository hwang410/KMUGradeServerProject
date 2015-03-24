# -*- coding: utf-8 -*-

from flask import request, render_template, url_for, redirect, session, flash
from sqlalchemy import func

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilPaging import get_page_pointed
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.utils import *

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
@GradeServer.route('/user_history/<memberId>/<sortCondition>?page<pageNum>')
@login_required
def user_history(memberId, sortCondition, pageNum):

    try:       
        # 총 제출 횟수 
        sumOfSubmissionCount = dao.query(func.count(Submissions.memberId).label('sumOfSubmissionCount')).\
                                   filter(Submissions.memberId == memberId).\
                                   subquery()
        # List Count
        count = dao.query(sumOfSubmissionCount).\
                    first().\
                    sumOfSubmissionCount  
        # 모든 제출 정보
        submissions = dao.query(Submissions.problemId,
                                Submissions.courseId, 
                                Submissions.status,
                                Submissions.score,
                                Submissions.sumOfSubmittedFileSize,
                                Submissions.runTime,
                                Submissions.usedLanguage,
                                Submissions.codeSubmissionDate).\
                          filter(Submissions.memberId == memberId).\
                          subquery()
        # Submit Language Join
        submissions = dao.query(submissions,
                                Languages.languageName).\
                          join(Languages, 
                                submissions.c.usedLanguage == Languages.languageIndex).\
                          subquery()
        # 중복 제거푼 문제숫
        sumOfSolvedProblemCount = dao.query(submissions).\
                                      group_by(submissions.c.problemId,
                                               submissions.c.courseId).\
                                      subquery()
                                      
        sumOfSolvedProblemCount = dao.query(func.count(sumOfSolvedProblemCount.c.problemId).label('sumOfSolvedProblemCount')).\
                                      filter(sumOfSolvedProblemCount.c.status == SOLVED).\
                                      subquery()
        # 모든 맞춘 횟수
        sumOfSolvedCount = dao.query(func.count(submissions.c.problemId).label('sumOfSolvedCount')).\
                               filter(submissions.c.status == SOLVED).\
                               subquery()
        # 틀린 횟수
        sumOfWrongAnswerCount = dao.query(func.count(submissions.c.problemId).label('sumOfWrongAnswerCount')).\
                                    filter(submissions.c.status == WRONG_ANSWER).\
                                    subquery()
        # 타임 오버 횟수
        sumOfTimeOverCount = dao.query(func.count(submissions.c.problemId).label('sumOfTimeOverCount')).\
                                 filter(submissions.c.status == TIME_OVER).\
                                 subquery()
        # 컴파일 에러 횟수
        sumOfCompileErrorCount = dao.query(func.count(submissions.c.problemId).label('sumOfCompileErrorCount')).\
                                     filter(submissions.c.status == COMPILE_ERROR).\
                                     subquery()
        # 런타임 에러 횟수
        sumOfRunTimeErrorCount = dao.query(func.count(submissions.c.problemId).label('sumOfRunTimeErrorCount')).\
                                     filter(submissions.c.status == RUN_TIME_ERROR).\
                                     subquery()
        # 서버 에러 횟수
        sumOfServerErrorCount = dao.query(func.count(submissions.c.problemId).label('sumOfServerErrorCount')).\
                                    filter(submissions.c.status == SERVER_ERROR).\
                                    subquery()
        # Viiew Value Text
        chartSubmissionDescriptions = ['맞춘 문제 갯수', '총 제출 횟수', '맞춘 횟수', '오답 횟수', '타임오버 횟수', '컴파일 에러 횟수', '런타임 에러 횟수', '서버 에러 횟수']

        try:                           
                # 모든 제출 정보
            submissionRecords = dao.query(Problems.problemName,
                                          submissions).\
                                    join(submissions,
                                         Problems.problemId == submissions.c.problemId).\
                                    subquery()
                # 제출날짜순 정렬
            if sortCondition == SUBMITTED_DATE:
                submissionRecords = dao.query(submissionRecords).\
                                        order_by(submissionRecords.c.codeSubmissionDate.desc()).\
                                        all()
            # 실행 시간 순 정렬
            elif sortCondition == RUN_TIME:
                submissionRecords = dao.query(submissionRecords).\
                                        order_by(submissionRecords.c.runTime.asc()).\
                                        all()
            # 코드 길이별 정렬
            else: # elif sortCondition == CODE_LENGTH:
                submissionRecords = dao.query(submissionRecords).\
                                        order_by(submissionRecords.c.sumOfSubmittedFileSize.asc()).\
                                        all()
        except Exception:
            #None Type Exception
            submissionRecords = []

        try:
                # 차트 정보
            chartSubmissionRecords = dao.query(sumOfSolvedProblemCount,
                                               sumOfSubmissionCount,
                                               sumOfSolvedCount,
                                               sumOfWrongAnswerCount,
                                               sumOfTimeOverCount,
                                               sumOfCompileErrorCount,
                                               sumOfRunTimeErrorCount,
                                               sumOfServerErrorCount).first()
        except Exception:
            #None Type Exception
            chartSubmissionRecords = []
        
        return render_template(USER_HISTORY_HTML,
                               memberId = memberId,
                               submissionRecords = submissionRecords,
                               chartSubmissionDescriptions = chartSubmissionDescriptions,
                               chartSubmissionRecords = chartSubmissionRecords,
                               pages = get_page_pointed(int(pageNum), count))
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
                memberId = session[MEMBER_ID]
                password = request.form['password']
                check = dao.query(Members.password).\
                            filter(Members.memberId == memberId).first()
                
                # 암호가 일치 할 때
                if check.password == password:#check_password_hash(password, check.password):

                    # for all user
                    if select == 'account':
                        return redirect(url_for(EDIT_PERSONAL))
                    # server manager
                    elif select == 'server_manage_problem':
                        return redirect(url_for('.server_manage_problem'))
                    elif select == 'server_manage_class':
                        return redirect(url_for('.server_manage_class'))
                    elif select == 'server_manage_user':
                        return redirect(url_for('.server_manage_user'))
                    elif select == 'server_manage_service':
                        return redirect(url_for('.server_manage_service'))
                    # class manager
                    elif select == 'user_submit':
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
            
    return render_template(ID_CHECK_HTML, error = error)

"""
로그인한 유저가 자신의 암호, 연락처 등을 바꿀수 있고
자신의 장보를 확인 할 수 있는 페이지
"""
@GradeServer.route('/edit_personal', methods = ['GET', 'POST'])
@login_required
def edit_personal(error = None):
    try:
        #Get User Information
        try:
            memberInformation = dao.query(DepartmentsDetailsOfMembers,
                                          Members.memberName,
                                          Members.contactNumber,
                                          Members.emailAddress,
                                          Members.comment,
                                          Colleges.collegeName,
                                          Departments.departmentName).\
                                    join(Colleges,
                                         Colleges.collegeIndex == DepartmentsDetailsOfMembers.collegeIndex).\
                                    join(Departments,
                                         Departments.departmentIndex == DepartmentsDetailsOfMembers.departmentIndex).\
                                    join(Members,
                                         Members.memberId == session[MEMBER_ID]).\
                                    filter(DepartmentsDetailsOfMembers.memberId == session[MEMBER_ID]).all()
            memberData = []
            loopIndex = 0
            for information in memberInformation:
                if loopIndex == 0:
                    memberData.append(information.memberName)
                    memberData.append(information.contactNumber)
                    memberData.append(information.emailAddress)
                    memberData.append(information.comment)
                    memberData.append(information.collegeName)
                    memberData.append(information.departmentName)
                else:
                    memberData.append(information.collegeName)
                    memberData.append(information.departmentName)
                loopIndex += 1   
            
        except Exception:
            #None Type Exception
            memberData = []
            
        #Get Post
        if request.method == 'POST':
            
            password = request.form['password']
            passwordConfirm = request.form['passwordConfirm'] 
            #Get Updating Data
            memberData[1] = contactNumber = request.form['contactNumber'] if request.form['contactNumber'] else memberData[1]
            memberData[2] = emailAddress = request.form['emailAddress'] if request.form['emailAddress'] else memberData[2]
            memberData[3] = comment = request.form['comment'] if request.form['comment'] else memberData[3]
            
            #Password Same
            if(password and passwordConfirm) and password == passwordConfirm:
                #Generate Password
                #password =generate_password_hash(password)
                passwordConfirm = None
                
                #Update DB
                dao.query(Members).\
                    filter(Members.memberId == session[MEMBER_ID]).\
                    update(dict(password = password,
                                contactNumber = contactNumber,
                                emailAddress = emailAddress,
                                comment =comment))
                # Commit Exception
                try:
                    dao.commit()
                    flash(get_message('updateSucceeded'))
                    
                    return redirect(url_for(SIGN_IN))
                except Exception:
                    dao.rollback()
                    error = get_message('upateFailed')
                
            #Password Different
            elif not password or not passwordConfirm:
                error = 'Confirm Password' + get_message('fillData')
            else:
                error = get_message('wrongPassword')
        
        return render_template(EDIT_PERSONAL_HTML,
                               memberInformation = memberData,
                               error = error)
    except Exception:
        return unknown_error()
    
""" ===== end Basic user space ===== """


""" ===== class master space ===== """

""" ===== end class master space ===== """

""" ===== server master space ===== """

""" ===== end server master space ===== """