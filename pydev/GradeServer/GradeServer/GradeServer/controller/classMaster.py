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
from sqlalchemy import and_, exc, or_, func
from datetime import datetime

import os
import re

projectPath = '/mnt/shared'
coursesPath = 'CurrentCourses'
limitedFileSize = 1024
DELETE = 'delete'
EDIT = 'edit'
TAB = 'Tab'
ADD = 'add'
ONE_FILE = 'OneFile'
MULTIPLE_FILES = 'MultipleFiles'
POST_METHOD = 'POST'
MEMBER_ID = 'memberId'

newUsers = []
newProblems = []

def get_own_problems(memberId):
    ownProblems = (dao.query(RegisteredProblems,
                             RegisteredCourses, 
                             Problems).\
                       join(RegisteredCourses, 
                            RegisteredCourses.courseId == RegisteredProblems.courseId).\
                       join(Problems, 
                            Problems.problemId == RegisteredProblems.problemId).\
                       filter(RegisteredCourses.courseAdministratorId == memberId)).\
                  all()
    return ownProblems

def get_own_courses(memberId):
    ownCourses = dao.query(RegisteredCourses).\
                     filter(RegisteredCourses.courseAdministratorId == memberId).\
                     all()
    return ownCourses

@GradeServer.route('/classmaster/user_submit')
@login_required
def class_user_submit():
    error = None
    
    try:
        ownCourses = get_own_courses(session[MEMBER_ID])
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
    global newProblems
    
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
        ownCourses = get_own_courses(session[MEMBER_ID])
    except:
        error = 'Error has been occurred while searching registered courses'
        return render_template('/class_manage_problem.html', 
                               error = error,
                               modalError = modalError, 
                               allProblems = allProblems, 
                               ownCourses = [], 
                               ownProblems = [])
    
    try:
        ownProblems = get_own_problems(session[MEMBER_ID])
    except:
        error = 'Error has been occurred while searching own problems'
        return render_template('/class_manage_problem.html', 
                               error = error,
                               modalError = modalError, 
                               allProblems = allProblems, 
                               ownCourses = ownCourses, 
                               ownProblems = [])
        
        
    if request.method == POST_METHOD:
        isNewProblem = True
        numberOfNewProblems = (len(request.form)-1)/7
        keys = {"courseId":"0", 
                "courseName":"1", 
                "problemId":"2", 
                "problemName":"3", 
                "multipleFiles":"4", 
                "startDate":"5", 
                "endDate":"6", 
                "openDate":"7", 
                "closeDate":"8"}
        
        # courseId, courseName, problemId, problemName, isAllInputCaseInOneFile, startDate, endDate, openDate, closeDate
        newProblem = [['' for i in range(9)] for j in range(numberOfNewProblems+1)]
        for form in request.form:
            if DELETE in form:
                isNewProblem = False
                courseId, problemId = form.split('_')[1:]
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
                    
            elif EDIT in form:
                isNewProblem = False
                editTarget, courseId, problemId, targetData = form[5:].split('_')
                targetData = request.form[form]

                # actually editTarget is 'id' value of tag. 
                # That's why it may have 'Tab' at the last of id to clarify whether it's 'all' tab or any tab of each course.
                # so when user pushes one of tab and modify the data, then we need to re-make the editTarget 
                if TAB in editTarget:
                    editTarget = editTarget[:-3]
                for registeredProblem, registeredCourse, problemName in ownProblems:
                    if registeredCourse.courseId == courseId and\
                       registeredProblem.problemId == int(problemId):
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
                if form == ADD:
                    continue
                value, index = re.findall('\d+|\D+', form)
                index = int(index)
                data = request.form[form]
                newProblem[index-1][int(keys[value])] = data
        
            
        # when 'add' button is pushed, insert new problem into RegisteredProblems table
        if isNewProblem:
            for index in range(numberOfNewProblems+1):
                newProblems.append(newProblem[index])
            
            for problem in newProblems:
                # if openDate, closeDate are empty then same with startDate, endDate
                if not problem[int(keys['openDate'])]:
                    problem[int(keys['openDate'])] = problem[int(keys['startDate'])]
                if not problem[int(keys['closeDate'])]:
                    problem[int(keys['closeDate'])] = problem[int(keys['endDate'])]
                if not problem[int(keys['multipleFiles'])]:
                    problem[int(keys['multipleFiles'])] = ONE_FILE
                else:
                    problem[int(keys['multipleFiles'])] = MULTIPLE_FILES
                problem[int(keys['courseId'])], problem[int(keys['courseName'])] = problem[int(keys['courseId'])].split(' ', 1)
                problem[int(keys['problemId'])], problem[int(keys['problemName'])] = problem[int(keys['problemId'])].split(' ', 1)
                try:
                    solutionCheckType = dao.query(Problems).\
                                            filter(Problems.problemId == problem[int(keys['problemId'])]).\
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
                    newProblem = RegisteredProblems(problemId = problem[int(keys['problemId'])],
                                                    courseId = problem[int(keys['courseId'])], 
                                                    solutionCheckType = solutionCheckType, 
                                                    isAllInputCaseInOneFile = problem[int(keys['multipleFiles'])],
                                                    limittedFileSize = limitedFileSize,
                                                    startDateOfSubmission = problem[int(keys['startDate'])],
                                                    endDateOfSubmission = problem[int(keys['endDate'])], 
                                                    openDate = problem[int(keys['openDate'])], 
                                                    closeDate = problem[int(keys['closeDate'])])
                    
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
                    newProblemRecord = SubmittedRecordsOfProblems(problemId = problem[int(keys['problemId'])],
                                                                  courseId = problem[int(keys['courseId'])])
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
                
                newProblems = []
                courseName = problem[int(keys['courseName'])].replace(' ', '')
                problemName = problem[int(keys['problemName'])].replace(' ', '')
                problemPath = '%s/%s/%s_%s/%s_%s' % (projectPath, 
                                                     coursesPath,
                                                     problem[int(keys['courseId'])], 
                                                     courseName, 
                                                     problem[int(keys['problemId'])], 
                                                     problemName)
                
                if not os.path.exists(problemPath):
                    os.makedirs(problemPath)
    
            return redirect(url_for('.class_manage_problem'))
    
    ownProblems = get_own_problems(session[MEMBER_ID])
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
                         filter(RegisteredCourses.courseAdministratorId == session[MEMBER_ID]).\
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
    
    if request.method == POST_METHOD:
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
                         filter(RegisteredCourses.courseAdministratorId == session[MEMBER_ID]).\
                         all()
    except:
        error = 'Error has been occurred while searching own courses'
        return render_template('/class_add_user.html', 
                               error = error, 
                               ownCourses = [],
                               allUsers = [],
                               allColleges = [],
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
    try:
        allUsers = dao.query(Members).\
                       filter(or_(Members.authority == "User",
                                  Members.authority == "CourseAdministrator")).\
                       subquery()
    except:
        error = 'Error has been occurred while searching all users'
        return render_template('/class_add_user.html', 
                               error = error, 
                               ownCourses = ownCourses,
                               allUsers = [],
                               allColleges = [],
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
    
    
    try:
        allColleges = dao.query(Colleges).\
                          all()
    except:
        error = 'Error has been occurred while searching all colleges'
        return render_template('/class_add_user.html', 
                               error = error, 
                               ownCourses = ownCourses,
                               allUsers = allUsers,
                               allColleges = [],
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
    try:
        allDepartments = dao.query(Departments).\
                             all()
    except:
        error = 'Error has been occurred while searching all departments'
        return render_template('/class_add_user.html', 
                               error = error, 
                               ownCourses = ownCourses,
                               allUsers = allUsers,
                               allColleges = allColleges,
                               allDepartments = allDepartments,
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
                        newUser[index - 1][3] = data.split()[0]
                        try:
                            newUser[index - 1][4] = dao.query(Colleges).\
                                                        filter(Colleges.collegeIndex == newUser[index - 1][3]).\
                                                        first().\
                                                        collegeName
                        except:
                            error = 'Wrong college index has inserted'
                            return render_template('/class_add_user.html', 
                                                   error = error, 
                                                   ownCourses = ownCourses,
                                                   allUsers = allUsers,
                                                   allColleges = allColleges,
                                                   allDepartments = allDepartments,
                                                   authorities = authorities,
                                                   newUsers = newUsers)
                    elif value == 'department':
                        newUser[index - 1][5] = data.split()[0]
                        try:
                            newUser[index - 1][6] = dao.query(Departments).\
                                                        filter(Departments.departmentIndex == newUser[index - 1][5]).\
                                                        first().\
                                                        departmentName
                        except:
                            error = 'Wrong department index has inserted'
                            return render_template('/class_add_user.html', 
                                                   error = error, 
                                                   ownCourses = ownCourses,
                                                   allUsers = allUsers,
                                                   allColleges = allColleges,
                                                   allDepartments = allDepartments,
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
                                                               allUsers = allUsers,
                                                               allColleges = allColleges,
                                                               allDepartments = allDepartments,
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
                                                   allUsers = allUsers,
                                                   allColleges = allColleges,
                                                   allDepartments = allDepartments,
                                                   authorities = authorities,
                                                   newUsers = newUsers)
                                    newUser[5] = value
                                    
                                elif key == 'courseId':
                                    try:
                                        newUser[7] = value.strip()
                                    except:
                                        error = 'Wrong course id has inserted'
                                        return render_template('/class_add_user.html',
                                                               error = error, 
                                                               ownCourses = ownCourses,
                                                               allUsers = allUsers,
                                                               allColleges = allColleges,
                                                               allDepartments = allDepartments,
                                                               authorities = authorities,
                                                               newUsers = newUsers)
                                    
                                else:
                                    error = 'Try again after check the manual'
                                    return render_template('/class_add_user.html', 
                                                           error = error, 
                                                           ownCourses = ownCourses,
                                                           allUsers = allUsers,
                                                           allColleges = allColleges,
                                                           allDepartments = allDepartments,
                                                           authorities = authorities,
                                                           newUsers = newUsers)
                                    
                            else:
                                error = 'Try again after check the manual'
                                return render_template('/class_add_user.html', 
                                                       error = error, 
                                                       ownCourses = ownCourses,
                                                       allUsers = allUsers,
                                                       allColleges = allColleges,
                                                       allDepartments = allDepartments,
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
                                                       allUsers = allUsers,
                                                       allColleges = allColleges,
                                                       allDepartments = allDepartments,
                                                       authorities = authorities,
                                                       newUsers = newUsers)
                                
                        newUsers.append(newUser)
                        
        elif 'addUser' in request.form:
            for newUser in newUsers:
                isExist = dao.query(Members).filter(Members.memberId == newUser[0]).first() 
                if not isExist:
                    try:
                        if newUser[2] == 'Course Admin':
                            newUser[2] = 'CourseAdministrator'
                                
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
                                               allUsers = allUsers,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments,
                                               authorities = authorities,
                                               newUsers = newUsers)
                        
                isExist = dao.query(Registrations).\
                              filter(and_(Registrations.memberId == newUser[0],
                                          Registrations.courseId == newUser[7].split()[0])).\
                              first()
                # new member
                if not isExist:
                    try:
                        # then insert to 'Registrations'.
                        freshman = Registrations(memberId = newUser[0],
                                                 courseId = newUser[7].split()[0])
                        dao.add(freshman)
                        dao.commit()
                    except:
                        dao.rollback()
                        error = 'Error has been occurred while registering new users'
                        return render_template('/class_add_user.html', 
                                               error = error, 
                                               ownCourses = ownCourses,
                                               allUsers = allUsers,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments,
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
                # old member
                else:
                    # suppose the user's department is different with his registered information
                    try:
                        departmentInformation = DepartmentsDetailsOfMembers(memberId = newUser[0],
                                                                            collegeIndex = newUser[3],
                                                                            departmentIndex =newUser[5])
                        dao.all(departmentInformation)
                        dao.commit()
                    except:
                        dao.rollback()
                
            newUsers = [] # initialize add user list
            return redirect(url_for('.class_manage_user'))
            
        elif 'deleteUser' in request.form:
            for form in request.form:
                if not form is 'deleteUser':
                    targetUserIdToDelete.append(form)
                                    
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
                           allUsers = allUsers,
                           allColleges = allColleges,
                           allDepartments = allDepartments,
                           authorities = authorities,
                           newUsers = newUsers)

@GradeServer.route('/classmaster/user_submit/summary')
@login_required
def user_submit_summary():
    error = None

    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter(RegisteredCourses.courseAdministratorId == session[MEMBER_ID]).\
                         all()
    except:
        return render_template('/class_user_submit_summary.html', 
                               error=error, 
                               ownCourses=[], 
                               ownProblems=[], 
                               ownMembers=[], 
                               submissions=[])
    try:       
        ownProblems = dao.query(RegisteredProblems).\
                          join(RegisteredCourses,
                               RegisteredProblems.courseId == RegisteredCourses.courseId).\
                          filter(RegisteredCourses.courseAdministratorId == session[MEMBER_ID]).\
                          all()
    except:
        return render_template('/class_user_submit_summary.html', 
                               error=error, 
                               ownCourses=ownCourses, 
                               ownProblems=[], 
                               ownMembers=[], 
                               submissions=[])     
    try:                 
        ownMembers = dao.query(Registrations).\
                         join(RegisteredCourses,
                              RegisteredCourses.courseId == Registrations.courseId).\
                         filter(RegisteredCourses.courseAdministratorId == session[MEMBER_ID]).\
                         all()
    except:
        return render_template('/class_user_submit_summary.html', 
                               error=error, 
                               ownCourses=ownCourses, 
                               ownProblems=ownProblems, 
                               ownMembers=[], 
                               submissions=[])                     
    try:
        submissions = dao.query(Submissions.memberId, Submissions.courseId, Submissions.problemId, func.max(Submissions.submissionCount).label("maxSubmissionCount")).\
                      group_by(Submissions.memberId, Submissions.courseId, Submissions.problemId).\
                      subquery()

        latestSubmissions = dao.query(Submissions).\
                                filter(Submissions.memberId == submissions.c.memberId,
                                       Submissions.courseId == submissions.c.courseId,
                                       Submissions.problemId == submissions.c.problemId,
                                       Submissions.submissionCount == submissions.c.maxSubmissionCount).\
                                all()
    except:
        print 'Submissions table is empty'
        submissions = []
    
    return render_template('/class_user_submit_summary.html', 
                           error=error, 
                           ownCourses=ownCourses, 
                           ownProblems=ownProblems, 
                           ownMembers=ownMembers, 
                           submissions=latestSubmissions)

@GradeServer.route('/classmaster/manage_service')
@login_required
def class_manage_service():
    # To do
    
    return render_template('/class_manage_service.html')
