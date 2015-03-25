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

from GradeServer.utils.utilMessages import get_message
from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilQuery import select_accept_courses, select_notices, select_match_member, select_top_coder
from GradeServer.utils.utils import *

from GradeServer.model.registrations import Registrations
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.submittedRecordsOfProblems import SubmittedRecordsOfProblems
from GradeServer.model.members import Members
from GradeServer.model.colleges import Colleges
from GradeServer.model.departments import Departments
from GradeServer.model.problems import Problems
from GradeServer.model.registeredProblems import RegisteredProblems
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.submissions import Submissions
from sqlalchemy import and_, exc
from datetime import datetime

import os
import re

projectPath = '/mnt/shared'
coursesPath = 'CurrentCourses'
newUsers = []

@GradeServer.route('/classmaster/user_submit')
@login_required
def class_user_submit():
    error = None
    
    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter_by(courseAdministratorId = session['memberId']).\
                         all()
    except:
        error = 'Error has been occurred while searching registered courses.'
        return render_template('/class_user_submit.html', 
                               error = error, 
                               ownCourses = [], 
                               submissions = [])
        
    try:
        submissions = (dao.query(Submissions,
                                 RegisteredCourses, 
                                 Problems).\
                           order_by(Submissions.codeSubmissionDate.desc()).\
                           group_by(Submissions.memberId, 
                                    Submissions.courseId, 
                                    Submissions.problemId).\
                           join(RegisteredCourses, 
                                RegisteredCourses.courseId == Submissions.courseId).\
                           join(Problems, 
                                Problems.problemId == Submissions.problemId)).\
                      all()
    except:
        error = 'Error has been occurred while searching submission records.'
        return render_template('/class_user_submit.html', 
                               error = error, 
                               ownCourses = ownCourses, 
                               submissions = [])
    
    return render_template('/class_user_submit.html', 
                           error = error, 
                           ownCourses = ownCourses, 
                           submissions = submissions)

@GradeServer.route('/classmaster/cm_manage_problem', methods=['GET', 'POST'])
@login_required
def class_manage_problem():
    global projectPath
    error = None
    modalError = None
    
    try:
        allProblems = dao.query(Problems).\
                          all()
    except:
        error = 'Error has been occurred while searching problems'
        return render_template('/class_manage_problem.html', 
                               error = error, 
                               modalError = error,
                               allProblems = [], 
                               ownCourses = [], 
                               ownProblems = [])
    
    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter_by(courseAdministratorId = session['memberId']).\
                         all()
    except:
        error = 'Error has been occurred while searching registered courses'
        return render_template('/class_manage_problem.html', 
                               error = error,
                               modalError = modalError, 
                               allProblems = allProblems, 
                               ownCourses = [], 
                               ownProblems = [])
    
    try:
        ownProblems = (dao.query(RegisteredProblems,
                                 RegisteredCourses, 
                                 Problems).\
                           join(RegisteredCourses, 
                                RegisteredCourses.courseId == RegisteredProblems.courseId).\
                           join(Problems, 
                                Problems.problemId == RegisteredProblems.problemId).\
                           filter(RegisteredCourses.courseAdministratorId == session['memberId'])).\
                      all()
        
    except:
        error = 'Error has been occurred while searching own problems'
        return render_template('/class_manage_problem.html', 
                               error = error,
                               modalError = modalError, 
                               allProblems = allProblems, 
                               ownCourses = ownCourses, 
                               ownProblems = [])
        
        
    if request.method == 'POST':
        courseId = problemId = 0
        isAllInputCaseInOneFile = 'OneFile'
        startDate = ''
        endDate = ''
        openDate = ''
        closeDate = ''
        isNewProblem = True
        
        for form in request.form:
            if 'delete' in form:
                isNewProblem = False
                courseId, problemId = form[7:].split('_')
                try:
                    targetProblem = dao.query(RegisteredProblems).\
                                        filter(and_(RegisteredProblems.courseId == courseId, 
                                                    RegisteredProblems.problemId == problemId)).\
                                        first()
                    dao.delete(targetProblem)
                    dao.commit()
                except:
                    dao.rollback()
                    error = 'Error has been occurred while searching the problem to delete'
                    return render_template('/class_manage_problem.html', 
                                           error = error, 
                                           modalError = modalError,
                                           allProblems = allProblems, 
                                           ownCourses = ownCourses, 
                                           ownProblems = ownProblems)
                    
            elif 'edit' in form:
                isNewProblem = False
                editTarget, courseId, problemId, targetData = form[5:].split('_')
                targetData = request.form[form]
                # actually editTarget is 'id' value of tag. 
                # That's why it may have 'Tab' at the last of id to clarify whether it's 'all' tab or any tab of each course.
                # so when user pushes one of tab and modify the data, then we need to remake the editTarget 
                if 'Tab' in editTarget:
                    editTarget = editTarget[:-3]
                for ownProblem in ownProblems:
                    if ownProblem.courseId == courseId and\
                       ownProblem.problemId == int(problemId):
                        kwargs = { editTarget : targetData }
                        try:
                            dao.query(RegisteredProblems).\
                                filter(and_(RegisteredProblems.courseId == courseId, 
                                            RegisteredProblems.problemId == problemId)).\
                                update(dict(**kwargs))
                            dao.commit()
                        except:
                            dao.rollback()
                            error = 'Error has been occurred while searching the problem to edit'
                            return render_template('/class_manage_problem.html', 
                                                   error = error, 
                                                   modalError = modalError,
                                                   allProblems = allProblems, 
                                                   ownCourses = ownCourses, 
                                                   ownProblems = ownProblems)
                        
            # addition problem
            else:
                startDate = request.form['startDate']
                endDate = request.form['endDate']
                openDate = request.form['openDate']
                closeDate = request.form['closeDate']
                courseId = int(request.form['courseId'][:10])
                limitedFileSize = 1024
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
            
            try:
                solutionCheckType = dao.query(Problems).\
                                        filter_by(problemId = problemId).\
                                        first().\
                                        solutionCheckType
            except:
                error = 'Error has been occurred while searching solution check type of the problem'
                return render_template('/class_manage_problem.html', 
                                       error = error, 
                                       modalError = modalError,
                                       allProblems = allProblems, 
                                       ownCourses = ownCourses, 
                                       ownProblems = ownProblems)
            
            try:
                print "id", problemId, 'cid', courseId, 'sct', solutionCheckType, 'icif', isAllInputCaseInOneFile, 'fs', limitedFileSize, 'st', startDate, 'ed', endDate, 'op', openDate, 'cd', closeDate
                newProblem = RegisteredProblems(problemId = problemId,
                                                courseId = courseId, 
                                                solutionCheckType = solutionCheckType, 
                                                isAllInputCaseInOneFile = isAllInputCaseInOneFile,
                                                limittedFileSize = limitedFileSize,
                                                startDateOfSubmission = startDate, 
                                                endDateOfSubmission = endDate, 
                                                openDate = openDate, 
                                                closeDate = closeDate)
                
                dao.add(newProblem)
                dao.commit()
            except:
                dao.rollback()
                error = 'Error has been occurred while making a new problem'
                return render_template('/class_manage_problem.html', 
                                       error = error, 
                                       modalError = modalError,
                                       allProblems = allProblems, 
                                       ownCourses = ownCourses, 
                                       ownProblems = ownProblems)
            try:
                newProblemRecord = SubmittedRecordsOfProblems(problemId = problemId,
                                                              courseId = courseId)
                dao.add(newProblemRecord)
                dao.commit()
            except:
                dao.rollback()
                error = 'Error has been occurred while creating new record'
                return render_template('/class_manage_problem.html', 
                           error = error, 
                           modalError = modalError,
                           allProblems = allProblems, 
                           ownCourses = ownCourses, 
                           ownProblems = ownProblems)
                
            courseName = request.form['courseId'][10:]
            problemName = request.form['problemId'][5:]
            problemPath = '%s/%s/%s_%s/%s_%s' % (projectPath, 
                                                 coursesPath,
                                                 courseId, 
                                                 courseName, 
                                                 problemId, 
                                                 problemName)
            
            if not os.path.exists(problemPath):
                os.makedirs(problemPath)
                
        return redirect(url_for('.class_manage_problem'))
        
    return render_template('/class_manage_problem.html', 
                           error = error, 
                           modalError = modalError,
                           allProblems = allProblems, 
                           ownCourses = ownCourses, 
                           ownProblems = ownProblems)

@GradeServer.route('/classmaster/cm_manage_user', methods=['GET', 'POST'])
@login_required
def class_manage_user():
    error = None
    
    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter_by(courseAdministratorId = session['memberId']).\
                         all()
    except:
        error = 'Error has been occurred while searching own courses'
        return render_template('/class_manage_user.html', 
                               error=error, 
                               ownCourses=[], 
                               ownUsers=[], 
                               allUsers=[], 
                               colleges=[],
                               departments=[])
    
    # all registered users
    allUsers = (dao.query(DepartmentsDetailsOfMembers, 
                          Members).\
                    join(Members, 
                         Members.memberId == DepartmentsDetailsOfMembers.memberId).\
                    filter(Members.authority == 'User').\
                    order_by(DepartmentsDetailsOfMembers.memberId)).\
               all()
    
    colleges = dao.query(Colleges).\
                   all()
    departments = dao.query(Departments).\
                      all()
    
    allUsersToData = []
    userIndex = 1
    loopIndex = 0
    for departmentsDetailsOfMember, eachUser in allUsers:
        if loopIndex == 0:
            allUsersToData.append([departmentsDetailsOfMember.memberId, 
                                   eachUser.memberName, 
                                   departmentsDetailsOfMember.collegeIndex, 
                                   departmentsDetailsOfMember.departmentIndex])
        else:
            if eachUser.memberId == allUsersToData[userIndex-1][0]:
                allUsersToData[userIndex-1].append(departmentsDetailsOfMember.collegeIndex)
                allUsersToData[userIndex-1].append(departmentsDetailsOfMember.departmentIndex)
            else:
                allUsersToData.append([departmentsDetailsOfMember.memberId, 
                                       eachUser.memberName, 
                                       departmentsDetailsOfMember.collegeIndex, 
                                       departmentsDetailsOfMember.departmentIndex])
                userIndex += 1
        loopIndex += 1
        
    ownUsers = []
    for ownCourse in ownCourses:
        try:
            ownUsersOfCourse = (dao.query(Registrations, 
                                          Members, 
                                          Colleges, 
                                          Departments).\
                                    join(Members, 
                                         Registrations.memberId == Members.memberId).\
                                    join(DepartmentsDetailsOfMembers, 
                                         DepartmentsDetailsOfMembers.memberId == Registrations.memberId).\
                                    join(Colleges, 
                                         Colleges.collegeIndex == DepartmentsDetailsOfMembers.collegeIndex).\
                                    join(Departments, 
                                         Departments.departmentIndex == DepartmentsDetailsOfMembers.departmentIndex).\
                                    filter(Registrations.courseId == ownCourse.courseId)).\
                               all()
        except:
            error = 'Error has been occurred while searching own users'
            return render_template('/class_manage_user.html', 
                                   error=error, 
                                   ownCourses=ownCourses, 
                                   ownUsers=[], 
                                   allUsers=[], 
                                   colleges=[],
                                   departments=[])
            
        for ownUser in ownUsersOfCourse:
            ownUsers.append(ownUser)
                
    ownUsersToData = []
    userIndex = 1
    loopIndex = 0
    for registration, eachUser, college, department in ownUsers:
        if loopIndex == 0:
            ownUsersToData.append([registration.courseId, 
                                   registration.memberId, 
                                   eachUser.memberName, 
                                   college.collegeName, 
                                   department.departmentName])
        else:
            if registration.memberId == ownUsersToData[userIndex-1][1] and registration.courseId == ownUsersToData[userIndex-1][0]:
                ownUsersToData[userIndex-1].append(college.collegeName)
                ownUsersToData[userIndex-1].append(department.departmentName)
            else:
                ownUsersToData.append([registration.courseId, 
                                       registration.memberId, 
                                       eachUser.memberName, 
                                       college.collegeName, 
                                       department.departmentName])
                userIndex += 1  
        loopIndex += 1
        
    if request.method == 'POST':
        for form in request.form:
            if 'delete' in form:
                courseId, memberId = form[7:].split('_')
                targetUser = dao.query(Registrations).\
                                 filter(and_(Registrations.courseId == courseId, 
                                             Registrations.memberId == memberId)).\
                                 first()
                dao.delete(targetUser)
                dao.commit()
            
        return redirect(url_for('.class_manage_user'))
    
    return render_template('/class_manage_user.html', 
                           error=error, 
                           ownCourses=ownCourses, 
                           ownUsers=ownUsersToData, 
                           allUsers=allUsersToData, 
                           colleges=colleges,
                           departments=departments)
    
@GradeServer.route('/classmaster/add_user', methods=['GET', 'POST'])
@login_required
def class_add_user():
    global newUsers
    error = None
    targetUserIdToDelete = []
    authorities = ['Course Admin', 'User']
    
    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter(RegisteredCourses.courseAdministratorId == session['memberId']).\
                         all()
    except:
        error = 'Error has been occurred while searching own courses'
        return render_template('/class_add_user.html', 
                               error = error, 
                               ownCourses = ownCourses,
                               authorities = authorities,
                               newUsers = newUsers)
    
    if request.method == 'POST':
        if 'addIndivisualUser' in request.form:
            # ( number of all form data - 'addIndivisualUser' form ) / forms for each person(id, name, college, department, authority)
            numberOfUsers = (len(request.form) - 1) / 5
            newUser = [['' for i in range(8)] for j in range(numberOfUsers + 1)]
            
            for form in request.form:
                if form != 'addIndivisualUser':
                    value, index = re.findall('\d+|\D+', form)
                    index = int(index)
                    data = request.form[form]
                    if value == 'userId':
                        newUser[index - 1][0] = data
                    elif value == 'username':
                        newUser[index - 1][1] = data
                    elif value == 'authority':
                        newUser[index - 1][2] = data
                    elif value == 'college':
                        newUser[index - 1][3] = data
                        try:
                            newUser[index - 1][4] = dao.query(Colleges).\
                                                        filter(Colleges.collegeIndex == data).\
                                                        first().\
                                                        collegeName
                        except:
                            error = 'Wrong college index has inserted'
                            return render_template('/class_add_user.html', 
                                                   error = error, 
                                                   ownCourses = ownCourses,
                                                   authorities = authorities,
                                                   newUsers = newUsers)
                    elif value == 'department':
                        newUser[index - 1][5] = data
                        try:
                            newUser[index - 1][6] = dao.query(Departments).\
                                                        filter(Departments.departmentIndex == data).\
                                                        first().\
                                                        departmentName
                        except:
                            error = 'Wrong department index has inserted'
                            return render_template('/class_add_user.html', 
                                                   error = error, 
                                                   ownCourses = ownCourses,
                                                   authorities = authorities,
                                                   newUsers = newUsers)
                    elif value == 'courseId':
                        newUser[index-1][7] = data.strip()
                        
            for index in range(numberOfUsers):
                newUsers.append(newUser[index])
                
        elif 'addUserGroup' in request.form:
            files = request.files.getlist('files')
            if list(files)[0].filename:
                # read each file
                for fileData in files:
                    # read each line    
                    for userData in fileData:
                        # slice and make information from 'key=value'
                        userInformation = userData.split(', ')
                        # userId, userName, authority, collegeIndex, collegeName, departmentIndex, departmentName
                        newUser = [''] * 8
                        
                        for eachData in userInformation:
                            if '=' in eachData:
                                # all authority is user in adding user from text file
                                newUser[2] = 'User'
                                key, value = eachData.split('=')
                                if key == 'userId':
                                    newUser[0] = value 
                                    
                                elif key == 'username':
                                    newUser[1] = value
                                    
                                elif key == 'college':
                                    try:
                                        newUser[4] = dao.query(Colleges).\
                                                         filter(Colleges.collegeIndex == value).\
                                                         first().\
                                                         collegeName
                                    except:
                                        error = 'Wrong college index has inserted'
                                        return render_template('/class_add_user.html', 
                                                               error = error, 
                                                               ownCourses = ownCourses,
                                                               authorities = authorities,
                                                               newUsers = newUsers)
                                    newUser[3] = value
                                       
                                elif key == 'department':
                                    try:
                                        newUser[6] = dao.query(Departments).\
                                                         filter(Departments.departmentIndex == value).\
                                                         first().\
                                                         departmentName
                                                         
                                    except:
                                        error = 'Wrong department index has inserted'
                                        return render_template('/class_add_user.html', 
                                                               error = error, 
                                                               ownCourses = ownCourses,
                                                               authorities = authorities,
                                                               newUsers = newUsers)
                                    newUser[5] = value
                                    
                                elif key == 'courseId':
                                    try:
                                        newUser[7] = value.strip()
                                        print newUser[7]
                                    except:
                                        error = 'Wrong course id has inserted'
                                        return render_template('/class_add_user.html',
                                                               error = error, 
                                                               ownCourses = ownCourses,
                                                               authorities = authorities,
                                                               newUsers = newUsers)
                                    
                                else:
                                    error = 'Try again after check the manual'
                                    return render_template('/class_add_user.html', 
                                                           error = error, 
                                                           ownCourses = ownCourses,
                                                           authorities = authorities,
                                                           newUsers = newUsers)
                                    
                            else:
                                error = 'Try again after check the manual'
                                return render_template('/class_add_user.html', 
                                                       error = error, 
                                                       ownCourses = ownCourses,
                                                       authorities = authorities,
                                                       newUsers = newUsers)
                        
                        for user in newUsers:
                            if user[0] == newUser[0] and\
                               user[3] == newUser[3] and\
                               user[5] == newUser[5]:
                                error = 'There is a duplicated user id. Check the file and added user list'
                                return render_template('/class_add_user.html', 
                                                       error = error, 
                                                       ownCourses = ownCourses,
                                                       authorities = authorities,
                                                       newUsers = newUsers)
                                
                        newUsers.append(newUser)
                        
        elif 'addUser' in request.form:
            for newUser in newUsers:
                isExist = dao.query(Members).filter(Members.memberId == newUser[0]).first() 
                if not isExist:
                    try:
                        # at first insert to 'Members'. Duplicated tuple will be ignored.
                        freshman = Members(memberId = newUser[0], 
                                           password = newUser[0], 
                                           memberName = newUser[1], 
                                           authority = newUser[2],
                                           signedInDate = datetime.now())
                        dao.add(freshman)
                        dao.commit()
                    except:
                        dao.rollback()
                        error = 'Error has been occurred while adding new users'
                        return render_template('/class_add_user.html', 
                                               error = error, 
                                               ownCourses = ownCourses,
                                               authorities = authorities,
                                               newUsers = newUsers)
                if not dao.query(Registrations).filter(Registrations.memberId == newUser[0]).first():
                    try:
                        # then insert to 'Registrations'.
                        freshman = Registrations(memberId = newUser[0],
                                                 courseId = newUser[7])
                        dao.add(freshman)
                        dao.commit()
                    except:
                        dao.rollback()
                        error = 'Error has been occurred while registering new users'
                        return render_template('/class_add_user.html', 
                                               error = error, 
                                               ownCourses = ownCourses,
                                               authorities = authorities,
                                               newUsers = newUsers)
                    
                    try:
                        departmentInformation = DepartmentsDetailsOfMembers(memberId = newUser[0], 
                                                                            collegeIndex = newUser[3], 
                                                                            departmentIndex = newUser[5])
                        dao.add(departmentInformation)
                        dao.commit()
                    except:
                        dao.rollback()
                        
                ## create user folder 
                newMemberId = newUser[0]
                targetCourseId = newUser[7]
                
                registeredProblems = (dao.query(RegisteredProblems, 
                                                Problems, 
                                                RegisteredCourses).\
                                          join(Problems, 
                                               Problems.problemId == RegisteredProblems.problemId).\
                                          join(RegisteredCourses,
                                               RegisteredCourses.courseId == RegisteredProblems.courseId).\
                                          filter(RegisteredProblems.courseId == targetCourseId)).\
                                     all()
                                        
                for registeredProblem, problem, registeredCourse in registeredProblems:
                    userFolderPath = '%s/%s/%s_%s/%s_%s/%s' % (projectPath,
                                                               coursesPath,
                                                               registeredProblem.courseId, 
                                                               registeredCourse.courseName, 
                                                               registeredProblem.problemId, 
                                                               problem.problemName, 
                                                               newMemberId)
                    os.makedirs(userFolderPath) if not os.path.exists(userFolderPath) else 0                 
                        
                ## creation end
            
            newUsers = [] # initialize add user list
            return redirect(url_for('.class_manage_user'))
            
        elif 'deleteUser' in request.form:
            for form in request.form:
                targetUserIdToDelete.append(form) if not form is 'deleteUser' else 0
                
        # if id list is not empty
        if len(targetUserIdToDelete) != 0:
            # each target user id
            for targetUser in targetUserIdToDelete:
                index = 0
                #print targetUser
                # each new user id
                for newUser in newUsers:
                    # if target id and new user id are same
                    if targetUser == newUser[0]:
                        del newUsers[index]
                        break
                    index += 1
                               
        
    return render_template('/class_add_user.html', 
                           error = error, 
                           ownCourses = ownCourses,
                           authorities = authorities,
                           newUsers = newUsers)

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
        submissions = (dao.query(Submissions, 
                                 Problems).\
                           order_by(Submissions.codeSubmissionDate.desc()).\
                           group_by(Submissions.memberId, 
                                    Submissions.courseId, 
                                    Submissions.problemId).\
                           join(RegisteredCourses, RegisteredCourses.courseId == Submissions.courseId).\
                           join(Problems, Problems.problemId == Submissions.problemId)).\
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
    # To do
    
    return render_template('/class_manage_service.html')