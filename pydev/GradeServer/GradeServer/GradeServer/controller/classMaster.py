# -*- coding: utf-8 -*-
"""
    GradeSever.controller.login
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    로그인 확인 데코레이터와 로그인 처리 모듈.

    :copyright: (c) 2015 by KookminUniv

"""

from flask import request, render_template, url_for, redirect, session

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils import login_required

from GradeServer.model.registrations import Registrations
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.members import Members
from GradeServer.model.colleges import Colleges
from GradeServer.model.departments import Departments
from GradeServer.model.problems import Problems
from GradeServer.model.registeredProblems import RegisteredProblems
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.submissions import Submissions

from sqlalchemy import and_, exc

import os

TRUE = 1
FALSE = 0

@GradeServer.route('/classmaster/<memberId>')
@login_required
def class_master_signin(memberId):
    return render_template('/class_master_signin.html')

@GradeServer.route('/classmaster/user_submit')
@login_required
def class_user_submit():
    error = None
    ownCourses = dao.query(RegisteredCourses).\
                     filter_by(courseAdministratorId = session['memberId']).\
                     all()
    try:
        submissions = dao.query(Submissions.courseId, 
                                Submissions.status, 
                                Submissions.submissionCount, 
                                Submissions.codeSubmissionDate,
                                RegisteredCourses.courseName, 
                                Problems.problemName).\
                                order_by(Submissions.codeSubmissionDate.desc()).\
                                                     group_by(Submissions.memberId, 
                                                              Submissions.courseId, 
                                                              Submissions.problemId).\
                                join(RegisteredCourses, 
                                     RegisteredCourses.courseId == Submissions.courseId).\
                                join(Problems, 
                                     Problems.problemId == Submissions.problemId).\
                                all()
    except:
        print "Submissions table is empty"
        submissions = []
    
    return render_template('/class_user_submit.html', 
                           error = error, 
                           ownCourses = ownCourses, 
                           submissions = submissions)

@GradeServer.route('/classmaster/cm_manage_problem', 
                   methods=['GET', 'POST'])
@login_required
def class_manage_problem():
    error = None
    allProblems = dao.query(Problems).\
                      all()
    ownCourses = dao.query(RegisteredCourses).\
                     filter_by(courseAdministratorId = session['memberId']).\
                     all()
    ownProblems = dao.query(RegisteredProblems.courseId, 
                            RegisteredProblems.isAllInputCaseInOneFile, 
                            RegisteredProblems.startDateOfSubmission,
                            RegisteredProblems.endDateOfSubmission, 
                            RegisteredProblems.openDate, 
                            RegisteredProblems.closeDate, 
                            RegisteredProblems.problemId,
                            RegisteredCourses.courseName, 
                            Problems.problemName).\
                      join(RegisteredCourses, 
                           RegisteredCourses.courseId == RegisteredProblems.courseId).\
                      join(Problems, 
                           Problems.problemId == RegisteredProblems.problemId).\
                      filter(RegisteredCourses.courseAdministratorId == session['memberId']).\
                      all()
    
    if request.method == 'POST':
        courseId = problemId = 0
        isAllInputCaseInOneFile = 'OneFile'
        startDate = ''
        endDate = ''
        openDate = ''
        closeDate = ''
        isNewProblem = TRUE
        
        for form in request.form:
            if 'delete' in form:
                isNewProblem = FALSE
                courseId, problemId = form[7:].split('_')
                targetProblem = dao.query(RegisteredProblems).\
                                    filter(and_(RegisteredProblems.courseId == courseId, 
                                                RegisteredProblems.problemId == problemId)).\
                                    first()
                dao.delete(targetProblem)
                dao.commit()
            elif 'edit' in form:
                isNewProblem = FALSE
                editTarget, courseId, problemId, targetData = form[5:].split('_')
                targetData = request.form[form]
                # actually editTarget is 'id' value of tag. 
                # That's why it may have 'Tab' at the last of id to clarify whether it's 'all' tab or any tab of each course.
                # so when user pushes one of tab and modify the data, then we need to remake the editTarget 
                if 'Tab' in editTarget:
                    editTarget = editTarget[:-3]
                for ownProblem in ownProblems:
                    if ownProblem.courseId == courseId and ownProblem.problemId == int(problemId):
                        kwargs = { editTarget : targetData }
                        dao.query(RegisteredProblems).\
                            filter(and_(RegisteredProblems.courseId == courseId, 
                                        RegisteredProblems.problemId == problemId)).\
                            update(dict(**kwargs))
                        dao.commit()
                        
            # addition problem
            else:
                startDate = request.form['startDate']
                endDate = request.form['endDate']
                openDate = request.form['openDate']
                closeDate = request.form['closeDate']
                courseId = int(request.form['courseId'][:10])
                problemId = int(request.form['problemId'][:5])
                if form == 'multipleFiles':
                    isAllInputCaseInOneFile = 'MultipleFiles'  
                
        # when 'add' button is pushed, insert new problem into RegisteredProblems table
        if isNewProblem:
            # if openDate, closeDate are empty then same with startDate, endDate
            if not openDate:
                openDate = startDate
            if not closeDate:
                closeDate = endDate
        
            solutionCheckType = dao.query(Problems).\
                                    filter_by(problemId = problemId).\
                                    first().\
                                    solutionCheckType
            newProblem = RegisteredProblems(problemId = problemId,
                                            courseId = courseId, 
                                            solutionCheckType = solutionCheckType, 
                                            isAllInputCaseInOneFile = isAllInputCaseInOneFile,
                                            startDateOfSubmission = startDate, 
                                            endDateOfSubmission = endDate, 
                                            openDate = openDate, 
                                            closeDate = closeDate)
            
            dao.add(newProblem)
            try:
                dao.commit()
            except:
                print 'addition error'
            
            courseName = request.form['courseId'][10:]
            problemName = request.form['problemId'][5:]
            problemPath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s' % (courseId, courseName, problemId, problemName)
            if not os.path.exists(problemPath):
                os.makedirs(problemPath)
                
        return redirect(url_for('.class_manage_problem'))
        
    return render_template('/class_manage_problem.html', 
                           error = error, 
                           allProblems = allProblems, 
                           ownCourses = ownCourses, 
                           ownProblems = ownProblems)

@GradeServer.route('/classmaster/cm_manage_user', 
                   methods=['GET', 'POST'])
@login_required
def class_manage_user():
    error = None
    ownCourses = dao.query(RegisteredCourses).\
                     filter_by(courseAdministratorId = session['memberId']).\
                     all()
    
    # all registered users
    allUsers = dao.query(DepartmentsDetailsOfMembers.memberId, 
                         DepartmentsDetailsOfMembers.collegeIndex, 
                         DepartmentsDetailsOfMembers.departmentIndex, 
                         Members.memberName).\
                   join(Members, Members.memberId == DepartmentsDetailsOfMembers.memberId).\
                   filter_by(authority = 'User').\
                   order_by(DepartmentsDetailsOfMembers.memberId).\
                   all()
    
    colleges = dao.query(Colleges).\
                   all()
    departments = dao.query(Departments).\
                      all()
    
    allUsersToData = []
    userIndex = 1
    for index, eachUser in enumerate(allUsers):
        if index == 0:
            allUsersToData.append([eachUser.memberId, 
                                   eachUser.memberName, 
                                   eachUser.collegeIndex, 
                                   eachUser.departmentIndex])
        else:
            if eachUser.memberId == allUsersToData[userIndex-1][0]:
                allUsersToData[userIndex-1].append(eachUser.collegeIndex)
                allUsersToData[userIndex-1].append(eachUser.departmentIndex)
            else:
                allUsersToData.append([eachUser.memberId, 
                                       eachUser.memberName, 
                                       eachUser.collegeIndex, 
                                       eachUser.departmentIndex])
                userIndex += 1
        
    ownUsers = []
    for ownCourse in ownCourses:
        try:
            ownUsersOfCourse = dao.query(Registrations.courseId, 
                                         Registrations.memberId, 
                                         Members.memberName, 
                                         Colleges.collegeName, 
                                         Departments.departmentName).\
                                   join(Members, 
                                        Registrations.memberId == Members.memberId).\
                                   join(DepartmentsDetailsOfMembers, 
                                        DepartmentsDetailsOfMembers.memberId == Registrations.memberId).\
                                   join(Colleges, 
                                        Colleges.collegeIndex == DepartmentsDetailsOfMembers.collegeIndex).\
                                   join(Departments, 
                                        Departments.departmentIndex == DepartmentsDetailsOfMembers.departmentIndex).\
                                   filter(Registrations.courseId == ownCourse.courseId).\
                                   all()
            for ownUser in ownUsersOfCourse:
                ownUsers.append(ownUser)
        except:
            print 'Registrations table is empty'
    
    ownUsersToData = []
    userIndex = 0
    for index, eachUser in enumerate(ownUsers):
        if index == 0:
            ownUsersToData.append([eachUser.courseId, 
                                   eachUser.memberId, 
                                   eachUser.memberName, 
                                   eachUser.collegeName, 
                                   eachUser.departmentName])
        else:
            if eachUser.memberId == ownUsersToData[userIndex-1][1] and eachUser.courseId == ownUsersToData[userIndex-1][0]:
                ownUsersToData[userIndex-1].append(eachUser.collegeName)
                ownUsersToData[userIndex-1].append(eachUser.departmentName)
            else:
                ownUsersToData.append([eachUser.courseId, 
                                       eachUser.memberId, 
                                       eachUser.memberName, 
                                       eachUser.collegeName, 
                                       eachUser.departmentName])
                userIndex += 1  
        
    if request.method == 'POST':
        newMemberId = ''
        targetCourseId = ''
        for form in request.form:
            if 'delete' in form:
                courseId, memberId = form[7:].split('_')
                targetUser = dao.query(Registrations).\
                                 filter(and_(Registrations.courseId == courseId, 
                                             Registrations.memberId == memberId)).\
                                 first()
                dao.delete(targetUser)
                dao.commit()
            else:
                newMemberId = request.form['memberId'].split()[0]
                targetCourseId = request.form['courseId'].split()[0]
                try:
                    newMember = Registrations(memberId = newMemberId, 
                                              courseId = targetCourseId)
                    dao.add(newMember)
                    dao.commit()
                
                except exc.SQLAlchemyError:
                    error = 'Exist duplicated students'
                    print error
                    return redirect(url_for('.class_manage_user'))
                 
                registeredProblems = dao.query(RegisteredProblems.problemId, 
                                               RegisteredProblems.courseId, 
                                               Problems.problemName, 
                                               RegisteredCourses.courseName).\
                                         join(Problems, 
                                              RegisteredProblems.problemId == Problems.problemId).\
                                         filter(RegisteredProblems.courseId == targetCourseId).\
                                         all()
                                        
                for registeredProblem in registeredProblems:
                    userFolderPath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s/%s' % (registeredProblem.courseId, 
                                                                                    registeredProblem.courseName, 
                                                                                    registeredProblem.problemId, 
                                                                                    registeredProblem.problemName, 
                                                                                    newMemberId)
                    if not os.path.exists(userFolderPath):                 
                        os.makedirs(userFolderPath)
            
        return redirect(url_for('.class_manage_user'))
    
    return render_template('/class_manage_user.html', 
                           error=error, 
                           ownCourses=ownCourses, 
                           ownUsers=ownUsersToData, 
                           allUsers=allUsersToData, 
                           colleges=colleges,
                           departments=departments)
""" ===== end class master space ===== """    

@GradeServer.route('/classmaster/user_submit/summary')
@login_required
def user_submit_summary():
    error = None
    ownCourses = dao.query(RegisteredCourses).\
                     filter_by(courseAdministratorId=session['memberId']).\
                     all()
    ownProblems = dao.query(RegisteredProblems).\
                      all()
    ownMembers = dao.query(Registrations).\
                     all()
        
    try:
        submissions = dao.query(Submissions.courseId, 
                                Problems.problemId, 
                                Submissions.status, 
                                Submissions.memberId).\
                          order_by(Submissions.codeSubmissionDate.desc()).\
                          group_by(Submissions.memberId, 
                                   Submissions.courseId, 
                                   Submissions.problemId).\
                          join(RegisteredCourses, RegisteredCourses.courseId == Submissions.courseId).\
                          join(Problems, Problems.problemId == Submissions.problemId).\
                          all()
    except:
        print 'Submissions table is empty'
        submissions = []
    
    return render_template('/class_user_submit_summary.html', 
                           error=error, 
                           ownCourses=ownCourses, 
                           ownProblems=ownProblems, 
                           ownMembers=ownMembers, 
                           submissions=submissions)

@GradeServer.route('/classmaster/manage_service')
@login_required
def class_manage_service():
    return render_template('/class_manage_service.html')