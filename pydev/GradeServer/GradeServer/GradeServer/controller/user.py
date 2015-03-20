# -*- coding: utf-8 -*-
from flask import request, render_template, url_for, redirect, session, flash
from sqlalchemy import func

from GradeServer.model.problems import Problems
from GradeServer.model.members import Members
from GradeServer.model.submissions import Submissions
from GradeServer.model.departments import Departments
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.colleges import Colleges
from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.controller.serverMaster import server_manage_problem, server_manage_class, server_manage_user, server_manage_service
from GradeServer.controller.classMaster import class_user_submit, class_manage_problem, class_manage_user, class_manage_service
from GradeServer.utils import login_required, get_page_pointed, unknown_error, get_message

@GradeServer.route('/users_submit_record')
@login_required
def users_submit_record():
    return render_template('/users_submit_record.html')

"""
로그인한 유저가 제출 했던 모든기록
"""
@GradeServer.route('/user_history/<memberId>/<sortCondition>?page<pageNum>')
@login_required
def user_history(memberId, sortCondition, pageNum):
    
    try :       
        # 총 제출 횟수 
        sumOfSubmissionCount = dao.query(func.count(Submissions.memberId).label("sumOfSubmissionCount")).\
                                   filter_by(memberId = memberId).\
                                   subquery()
            
        count =dao.query(sumOfSubmissionCount).\
                   first().\
                   sumOfSubmissionCount    
        # 모든 제출 정보
        submissions =dao.query(Submissions.problemId, 
                               Submissions.courseId, 
                               Submissions.status, 
                               Submissions.score, 
                               Submissions.sumOfSubmittedFileSize,
                               Submissions.runTime, 
                               Submissions.usedLanguage, 
                               Submissions.codeSubmissionDate).\
                               filter_by(memberId = memberId).\
                               subquery()
        # 제출날짜순 정렬
        if sortCondition == 'submittedDate':
            submissions = dao.query(Problems.problemName, 
                                    submissions).\
                              join(submissions, 
                                   Problems.problemId == submissions.c.problemId).\
                              order_by(submissions.c.codeSubmissionDate.desc()).\
                              subquery()
        # 실행 시간 순 정렬
        elif sortCondition == 'runTime':
            submissions = dao.query(Problems.problemName, 
                                    submissions).\
                              join(submissions, 
                                   Problems.problemId == submissions.c.problemId).\
                              order_by(submissions.c.runTime.asc()).\
                              subquery()
        # 코드 길이별 정렬
        else : # sortCondition == "codeLength" 
            submissions = dao.query(Problems.problemName, 
                                    submissions).\
                              join(submissions, 
                                   Problems.problemId == submissions.c.problemId).\
                              order_by(submissions.c.sumOfSubmittedFileSize.asc()).\
                              subquery()
        # 중복 제거푼 문제숫
        sumOfSolvedProblemCount = dao.query(func.count(submissions.c.problemId).label('sumOfSolvedProblemCount')).\
                                      filter(submissions.c.status == 'Solved').\
                                      group_by(submissions.c.problemId, 
                                               submissions.c.courseId).\
                                      subquery()
        # 모든 맞춘 횟수
        sumOfSolvedCount = dao.query(func.count(submissions.c.problemId).label('sumOfSolvedCount')).\
                               filter(submissions.c.status == 'Solved').\
                               subquery()
        # 틀린 횟수
        sumOfWrongAnswerCount = dao.query(func.count(submissions.c.problemId).label('sumOfWrongAnswerCount')).\
                                    filter(submissions.c.status == 'WrongAnswer').\
                                    subquery()
        # 타임 오버 횟수
        sumOfTimeOverCount = dao.query(func.count(submissions.c.problemId).label('sumOfTimeOverCount')).\
                                 filter(submissions.c.status == 'TimeOver').\
                                 subquery()
        # 컴파일 에러 횟수
        sumOfCompileErrorCount = dao.query(func.count(submissions.c.problemId).label('sumOfCompileErrorCount')).\
                                     filter(submissions.c.status == 'CompileError').\
                                     subquery()
        # 런타임 에러 횟수
        sumOfRunTimeErrorCount = dao.query(func.count(submissions.c.problemId).label('sumOfRunTimeErrorCount')).\
                                     filter(submissions.c.status == 'RunTimeError').\
                                     subquery()
        # 서버 에러 횟수
        sumOfServerErrorCount = dao.query(func.count(submissions.c.problemId).label('sumOfServerErrorCount')).\
                                    filter(submissions.c.status == 'ServerError').\
                                    subquery()
        chartSubmissionDescriptions = ['맞춘 문제 갯수', 
                                             '총 제출 횟수', 
                                             '맞춘 횟수', 
                                             '오답 횟수', 
                                             '타임오버 횟수', 
                                             '컴파일 에러 횟수', 
                                             '런타임 에러 횟수', 
                                             '서버 에러 횟수']
        
        try :                           
            # 모든 제출 정보
            submissionRecords = dao.query(submissions).all()
            # 차트 정보
            chartSubmissionRecords = dao.query(sumOfSolvedProblemCount, 
                                               sumOfSubmissionCount, 
                                               sumOfSolvedCount, 
                                               sumOfWrongAnswerCount,
                                               sumOfTimeOverCount, 
                                               sumOfCompileErrorCount, 
                                               sumOfRunTimeErrorCount, 
                                               sumOfServerErrorCount).\
                                         first()
        except Exception :
            #None Type Exception
            submissionRecords = []
            chartSubmissionRecords = []
            
        return render_template('/user_history.html', 
                               memberId = memberId,
                               submissionRecords = submissionRecords,
                               chartSubmissionDescriptions = chartSubmissionDescriptions,
                               chartSubmissionRecords = chartSubmissionRecords,
                               pages = get_page_pointed(int(pageNum), count))
    except Exception :
        # Unknow Error
        return unknown_error()

"""
로그인한 유저가 권한이 필요한 페이지에 접급하기전
본인인지 확인하기 위한 페이지
"""
@GradeServer.route('/id_check/<select>', 
                   methods = ['GET', 'POST'])
@login_required
def id_check(select, error = None):
    if request.method == 'POST':
        # 암호를 입력 안했을 때
        if not request.form['password']:
            error = get_message('fillPassword')
        else:
            try:
                memberId = session['memberId']
                password = request.form['password']
                check = dao.query(Members.password).\
                            filter_by(memberId = memberId).\
                            first()

                # 암호가 일치 할 때
                if check.password == password:#check_password_hash (password, check.password):
                    # for all user
                    if select == 'account':
                        return redirect(url_for('.edit_personal'))
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
            except Exception as e :
                Log.error(str(e))
                raise e
            
    return render_template('/id_check.html', 
                           error = error)

"""
로그인한 유저가 자신의 암호, 연락처 등을 바꿀수 있고
자신의 장보를 확인 할 수 있는 페이지
"""
@GradeServer.route('/edit_personal', 
                   methods = ['GET', 'POST'])
@login_required
def edit_personal(error = None):
    try :
        #Get User Information
        try :
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
                                         Members.memberId==session['memberId']).\
                                    filter(DepartmentsDetailsOfMembers.memberId == session['memberId']).\
                                    all()
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
            
        except Exception :
            #None Type Exception
            memberData = []
            
        #Get Post
        if request.method == 'POST':
            password =request.form['password']
            passwordConfirm =request.form['passwordConfirm'] 
            #Get Updating Data
            memberData[1] = contactNumber = request.form['contactNumber'] if request.form['contactNumber'] else memberData[1]
            memberData[2] = emailAddress = request.form['emailAddress'] if request.form['emailAddress'] else memberData[2]
            memberData[3] = comment =request.form['comment'] if request.form['comment'] else memberData[3]
            
            #Password Same
            if (password and passwordConfirm ) and password == passwordConfirm:
                #Generate Password
                #password =generate_password_hash (password)
                passwordConfirm = None
                
                #Update DB
                dao.query(Members).\
                    filter_by(memberId = session['memberId']).\
                    update(dict(password = password, 
                                contactNumber = contactNumber, 
                                emailAddress = emailAddress, 
                                comment = comment))
                # Commit Exception
                try :
                    dao.commit()
                    flash(get_message('updateSuccessed'))
                    
                    return redirect(url_for('.sign_in'))
                except Exception :
                    dao.rollback()
                    error = get_message('upateFailed')
                
            #Password Different
            elif not password or not passwordConfirm:
                error = get_message('fillConfirmPassword')
            else:
                error = get_message('wrongPassword')
        
        return render_template('/edit_personal.html', 
                               error = error,
                               memberInformation = memberData)
    except Exception :
        return unknown_error()