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

from GradeServer.utils.loginRequired import login_required

from GradeServer.model.registrations import Registrations
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.submittedRecordsOfProblems import SubmittedRecordsOfProblems
from GradeServer.model.members import Members
from GradeServer.model.colleges import Colleges
from GradeServer.model.departments import Departments
from GradeServer.model.departmentsOfColleges import DepartmentsOfColleges
from GradeServer.model.problems import Problems
from GradeServer.model.registeredProblems import RegisteredProblems
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.submissions import Submissions
from sqlalchemy import and_,or_,func
from datetime import datetime

from GradeServer.resource.setResources import SETResources
from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.otherResources import OtherResources

import os
import re
import glob
from __builtin__ import False

projectPath = '/mnt/shared'
problemsPath = '%s/Problems' % projectPath
coursesPath = 'CurrentCourses'
limitedFileSize = 1024
DELETE = 'delete'
EDIT = 'edit'
TAB = 'Tab'
ADD = 'add'
ONE_FILE = 'OneFile'
MULTIPLE_FILES = 'MultipleFiles'
POST_METHOD = 'POST'

newUsers = []
newProblems = []

def get_case_count(problemCasesPath, multipleFiles):
    caseCount = len(glob.glob(os.path.join(problemCasesPath, '*.*')))/2
    
    if caseCount > 1:
        if multipleFiles == ENUMResources().const.FALSE:
            caseCount -= 1
        else:
            caseCount = 1
    return caseCount

def get_own_problems(memberId):
    ownProblems = (dao.query(RegisteredProblems,
                             RegisteredCourses,
                             Problems).\
                       join(RegisteredCourses,
                            RegisteredCourses.courseId == RegisteredProblems.courseId).\
                       join(Problems,
                            Problems.problemId == RegisteredProblems.problemId).\
                       filter(and_(RegisteredCourses.courseAdministratorId == memberId,
                                   Problems.isDeleted == ENUMResources().const.FALSE))).\
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
    # moved from URL, error will occur
    if request.referrer.rsplit('/', 1)[1] != "user_submit":
        error = "invalid access"
        print error
        
    error = None
    
    try:
        ownCourses = get_own_courses(session[SessionResources().const.MEMBER_ID])
    except:
        error = 'Error has been occurred while searching registered courses.'
        return render_template('/class_user_submit.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
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
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               ownCourses = ownCourses,
                               submissions = [])
    
    return render_template('/class_user_submit.html',
                           error = error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           ownCourses = ownCourses,
                           submissions = submissions)

@GradeServer.route('/classmaster/cm_manage_problem',methods=['GET','POST'])
@login_required
def class_manage_problem():
    # moved from URL, error will occur
    if request.referrer.rsplit('/', 1)[1] != "cm_manage_problem":
        error = "invalid access"
        print error
        
    global projectPath
    global newProblems
    
    error = None
    modalError = None
    
    try:
        allProblems = dao.query(Problems).\
                          filter(Problems.isDeleted == ENUMResources().const.FALSE).\
                          all()
    except:
        error = 'Error has been occurred while searching problems'
        return render_template('/class_manage_problem.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               modalError = error,
                               allProblems = [],
                               ownCourses = [],
                               ownProblems = [])
    
    try:
        ownCourses = get_own_courses(session[SessionResources().const.MEMBER_ID])
    except:
        error = 'Error has been occurred while searching registered courses'
        return render_template('/class_manage_problem.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               modalError = modalError,
                               allProblems = allProblems,
                               ownCourses = [],
                               ownProblems = [])

    try:
        ownProblems = get_own_problems(session[SessionResources().const.MEMBER_ID])
    except:
        error = 'Error has been occurred while searching own problems'
        return render_template('/class_manage_problem.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               modalError = modalError,
                               allProblems = allProblems,
                               ownCourses = ownCourses,
                               ownProblems = [])
        
    if request.method == POST_METHOD:
        isNewProblem = True
        numberOfNewProblems = (len(request.form)-1)/7
        keys = {"courseId":0,
                "courseName":1,
                "problemId":2,
                "problemName":3,
                "isAllInputCaseInOneFile":4,
                "startDate":5,
                "endDate":6,
                "openDate":7,
                "closeDate":8}
        
        # courseId,courseName,problemId,problemName,isAllInputCaseInOneFile,startDate,endDate,openDate,closeDate
        newProblem = [['' for i in range(9)] for j in range(numberOfNewProblems+1)]
        for form in request.form:

            if DELETE in form:
                isNewProblem = False
                courseId,problemId = form.split('_')[1:]
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
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           modalError = modalError,
                                           allProblems = allProblems,
                                           ownCourses = ownCourses,
                                           ownProblems = ownProblems)
                    
            elif EDIT in form:
                isNewProblem = False
                editTarget,courseId,problemId,targetData = form[5:].split('_')
                targetData = request.form[form]

                # actually editTarget is 'id' value of tag. 
                # That's why it may have 'Tab' at the last of id to clarify whether it's 'all' tab or any tab of each course.
                # so when user pushes one of tab and modify the data,then we need to re-make the editTarget 
                if TAB in editTarget:
                    editTarget = editTarget[:-3]
                for registeredProblem,registeredCourse,problemName in ownProblems:
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
                                                   SETResources = SETResources,
                                                   SessionResources = SessionResources,
                                                   modalError = modalError,
                                                   allProblems = allProblems,
                                                   ownCourses = ownCourses,
                                                   ownProblems = ownProblems)
                        
            # addition problem
            else:
                if form == ADD:
                    continue
                value,index = re.findall('\d+|\D+',form)
                index = int(index)
                data = request.form[form]
                newProblem[index-1][keys[value]] = data
        
        # when 'add' button is pushed,insert new problem into RegisteredProblems table
        if isNewProblem:
            for index in range(numberOfNewProblems+1):
                newProblems.append(newProblem[index])
            for problem in newProblems:
                # if openDate,closeDate are empty then same with startDate,endDate
                if not problem[keys['openDate']]:
                    problem[keys['openDate']] = problem[keys['startDate']]
                if not problem[keys['closeDate']]:
                    problem[keys['closeDate']] = problem[keys['endDate']]
                if not problem[keys['isAllInputCaseInOneFile']]:
                    problem[keys['isAllInputCaseInOneFile']] = ENUMResources().const.FALSE
                else:
                    problem[keys['isAllInputCaseInOneFile']] = ENUMResources().const.TRUE
                if problem[keys['courseId']]:
                    problem[keys['courseId']],problem[keys['courseName']] = problem[keys['courseId']].split(' ',1)
                if problem[keys['problemId']]:
                    problem[keys['problemId']],problem[keys['problemName']] = problem[keys['problemId']].split(' ',1)
                    try:
                        solutionCheckType = dao.query(Problems).\
                                                filter(Problems.problemId == problem[keys['problemId']]).\
                                                first().solutionCheckType
                    except:
                        error = "error has been occurred while getting solution check type"
                        return render_template('/class_manage_problem.html',
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               modalError = modalError,
                                               allProblems = allProblems,
                                               ownCourses = ownCourses,
                                               ownProblems = ownProblems)
                    
                    pathOfTestCase = '%s/%s_%s/%s_%s' % (problemsPath,
                                                         problem[keys['problemId']],
                                                         problem[keys['problemName']],
                                                         problem[keys['problemName']],
                                                         solutionCheckType)
                
                    numberOfTestCase = get_case_count(pathOfTestCase, problem[keys['isAllInputCaseInOneFile']])
                    
                # validation check before insert new problem
                isValid = True
                for key in problem:
                    if not key:
                        isValid = False
                        break
                if not isValid:
                    continue

                try:
                    newProblem = RegisteredProblems(problemId = problem[keys['problemId']],
                                                    courseId = problem[keys['courseId']],
                                                    isAllInputCaseInOneFile = problem[keys['isAllInputCaseInOneFile']],
                                                    limittedFileSize = limitedFileSize,
                                                    numberOfTestCase = numberOfTestCase,
                                                    startDateOfSubmission = problem[keys['startDate']],
                                                    endDateOfSubmission = problem[keys['endDate']],
                                                    openDate = problem[keys['openDate']],
                                                    closeDate = problem[keys['closeDate']])
                    
                    dao.add(newProblem)
                    dao.commit()
                except:
                    dao.rollback()
                    error = 'Error has been occurred while making a new problem'
                    return render_template('/class_manage_problem.html',
                                           error = error, 
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           modalError = modalError,
                                           allProblems = allProblems,
                                           ownCourses = ownCourses,
                                           ownProblems = ownProblems)

                try:
                    newProblemRecord = SubmittedRecordsOfProblems(problemId = problem[keys['problemId']],
                                                                  courseId = problem[keys['courseId']])
                    dao.add(newProblemRecord)
                    dao.commit()
                except:
                    dao.rollback()
                    error = 'Error has been occurred while creating new record'
                    return render_template('/class_manage_problem.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               modalError = modalError,
                               allProblems = allProblems,
                               ownCourses = ownCourses,
                               ownProblems = ownProblems)

            newProblems = []
                
            return redirect(url_for('.class_manage_problem'))
        
    ownProblems = get_own_problems(session[SessionResources().const.MEMBER_ID])
    return render_template('/class_manage_problem.html',
                           error = error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           modalError = modalError,
                           allProblems = allProblems,
                           ownCourses = ownCourses,
                           ownProblems = ownProblems)

@GradeServer.route('/classmaster/cm_manage_user',methods=['GET','POST'])
@login_required
def class_manage_user():
    # moved from URL, error will occur
    if request.referrer.rsplit('/', 1)[1] != "cm_manage_user":
        error = "invalid access"
        print error
        
    error = None
    
    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID]).\
                         all()
    except:
        error = 'Error has been occurred while searching own courses'
        return render_template('/class_manage_user.html',
                               error=error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
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
                    filter(Members.authority == SETResources().const.USER).\
                    order_by(DepartmentsDetailsOfMembers.memberId)).\
               all()

    colleges = dao.query(Colleges).\
                   all()
    departments = dao.query(Departments).\
                      all()
                      
    allUsersToData = []
    userIndex = 1
    loopIndex = 0
    for departmentsDetailsOfMember,eachUser in allUsers:
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
                                    filter(Registrations.courseId == ownCourse.courseId).\
                                    order_by(Members.memberId)).\
                               all()
        except:
            error = 'Error has been occurred while searching own users'
            return render_template('/class_manage_user.html',
                                   error=error, 
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
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
    for registration,eachUser,college,department in ownUsers:
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
                courseId,memberId = form[7:].split('_')
                targetUser = dao.query(Registrations).\
                                 filter(and_(Registrations.courseId == courseId,
                                             Registrations.memberId == memberId)).\
                                 first()
                dao.delete(targetUser)
                dao.commit()
            
        return redirect(url_for('.class_manage_user'))
    
    return render_template('/class_manage_user.html',
                           error=error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           ownCourses=ownCourses,
                           ownUsers=ownUsersToData,
                           allUsers=allUsersToData,
                           colleges=colleges,
                           departments=departments)
    
@GradeServer.route('/classmaster/add_user',methods=['GET','POST'])
@login_required
def class_add_user():
    # moved from URL, error will occur
    if request.referrer.rsplit('/', 1)[1] != "add_user":
        error = "invalid access"
        print error
        
    global newUsers
    error = None
    targetUserIdToDelete = []
    authorities = ['Course Admin','User']
    keys = {'memberId':0,
            'memberName':1,
            'authority':2,
            'collegeIndex':3,
            'collegeName':4,
            'departmentIndex':5,
            'departmentName':6,
            'courseId':7}
    
    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID]).\
                         all()
    except:
        error = 'Error has been occurred while searching own courses'
        return render_template('/class_add_user.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               ownCourses = [],
                               allUsers = [],
                               allColleges = [],
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
    try:
        allUsers = dao.query(Members).\
                       filter(or_(Members.authority == SETResources().const.USER,
                                  Members.authority == SETResources().const.COURSE_ADMINISTRATOR))
    except:
        error = 'Error has been occurred while searching all users'
        return render_template('/class_add_user.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
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
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               ownCourses = ownCourses,
                               allUsers = allUsers,
                               allColleges = [],
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
    try:
        allDepartments = (dao.query(DepartmentsOfColleges,
                                    Colleges,
                                    Departments).\
                              join(Colleges,
                                   Colleges.collegeIndex == DepartmentsOfColleges.collegeIndex).\
                              join(Departments,
                                   Departments.departmentIndex == DepartmentsOfColleges.departmentIndex)).\
                         all()
    except:
        error = 'Error has been occurred while searching all departments'
        return render_template('/class_add_user.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               ownCourses = ownCourses,
                               allUsers = allUsers,
                               allColleges = allColleges,
                               allDepartments = allDepartments,
                               authorities = authorities,
                               newUsers = newUsers)
    
    if request.method == 'POST':
        if 'addIndivisualUser' in request.form:
            # ( number of all form data - 'addIndivisualUser' form ) / forms for each person(id,name,college,department,authority)
            numberOfUsers = (len(request.form) - 1) / 5
            newUser = [['' for i in range(8)] for j in range(numberOfUsers + 1)]
            for form in request.form:
                if form != 'addIndivisualUser':
                    value,index = re.findall('\d+|\D+',form)
                    index = int(index)
                    data = request.form[form]
                    if value == 'userId':
                        newUser[index - 1][keys['memberId']] = data
                    elif value == 'username':
                        newUser[index - 1][keys['memberName']] = data
                    elif value == 'authority':
                        newUser[index - 1][keys['authority']] = data
                    elif value == 'college':
                        newUser[index - 1][keys['collegeIndex']] = data.split()[0]
                        # actually data.split()[1] is collegeName but it can be wrong, 
                        # so, here for checking the index is valid.
                        try:
                            newUser[index - 1][keys['collegeName']] =\
                                dao.query(Colleges).\
                                    filter(Colleges.collegeIndex == newUser[index - 1][keys['collegeIndex']]).\
                                    first().\
                                    collegeName
                        except:
                            pass
                        
                    elif value == 'department':
                        newUser[index - 1][keys['departmentIndex']] = data.split()[0]
                        try:
                            newUser[index - 1][keys['departmentName']] =\
                                dao.query(Departments).\
                                    filter(Departments.departmentIndex == newUser[index - 1][keys['departmentIndex']]).\
                                    first().\
                                    departmentName
                        except:
                            pass
                            
                    elif value == 'courseId':
                        newUser[index-1][keys['courseId']] = data.strip()
                        
            for index in range(numberOfUsers):
                isValid = True
                for value in newUser[index]:
                    if not value:
                        isValid = False
                        pass
                if isValid:
                    newUsers.append(newUser[index])
                
        elif 'addUserGroup' in request.form:
            files = request.files.getlist('files')
            courseId = request.form['courseId'].split()[0]

            if list(files)[0].filename:
                # read each file
                for fileData in files:
                    # read each line    
                    for userData in fileData:
                        # slice and make information from 'key=value'
                        userInformation = userData.replace(' ', '').replace('\n', '').replace('\xef\xbb\xbf', '').split(',')
                        
                        # userId,userName,authority,collegeIndex,collegeName,departmentIndex,departmentName
                        newUser = [''] * 8
                        
                        # all authority is user in adding user from text file
                        newUser[keys['authority']] = SETResources().const.USER
                        newUser[keys['courseId']] = courseId
                        
                        for eachData in userInformation:
                            if '=' in eachData:
                                key, value = eachData.split('=')
                                
                                if key == 'userId':
                                    newUser[keys['memberId']] = value 
                                    
                                elif key == 'username':
                                    newUser[keys['memberName']] = value
                                    
                                elif key == 'college':
                                    newUser[keys['collegeIndex']] = value
                                    try:
                                        newUser[keys['collegeName']] = dao.query(Colleges).\
                                                                           filter(Colleges.collegeIndex == value).\
                                                                           first().\
                                                                           collegeName
                                    except:
                                        pass
                                       
                                elif key == 'department':
                                    newUser[keys['departmentIndex']] = value
                                    try:
                                        newUser[keys['departmentName']] = dao.query(Departments).\
                                                                              filter(Departments.departmentIndex == value).\
                                                                              first().\
                                                                              departmentName
                                                         
                                    except:
                                        pass
                                                                      
                                else:
                                    error = 'Try again after check the manual'
                                    return render_template('/class_add_user.html',
                                                           error = error, 
                                                           SETResources = SETResources,
                                                           SessionResources = SessionResources,
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
                                                       SETResources = SETResources,
                                                       SessionResources = SessionResources,
                                                       ownCourses = ownCourses,
                                                       allUsers = allUsers,
                                                       allColleges = allColleges,
                                                       allDepartments = allDepartments,
                                                       authorities = authorities,
                                                       newUsers = newUsers)
                        
                        for user in newUsers:
                            if user[keys['memberId']] == newUser[keys['memberId']] and\
                               user[keys['collegeIndex']] == newUser[keys['collegeIndex']] and\
                               user[keys['departmentIndex']] == newUser[keys['departmentIndex']]:
                                error = 'There is a duplicated user id. Check the file and added user list'
                                return render_template('/class_add_user.html',
                                                       error = error, 
                                                       SETResources = SETResources,
                                                       SessionResources = SessionResources,
                                                       ownCourses = ownCourses,
                                                       allUsers = allUsers,
                                                       allColleges = allColleges,
                                                       allDepartments = allDepartments,
                                                       authorities = authorities,
                                                       newUsers = newUsers)
                        
                        isValid = True
                        for key in newUser:
                            if key == '':
                                isValid = False
                                break
                        if isValid:
                            newUsers.append(newUser)
                        
        elif 'addUser' in request.form:
            for newUser in newUsers:
                isExist = dao.query(Members).filter(Members.memberId == newUser[0]).first() 
                if not isExist:
                    try:
                        if newUser[keys['authority']] == 'Course Admin':
                            newUser[keys['authority']] = SETResources().const.COURSE_ADMINISTRATOR
                                
                        # at first insert to 'Members'. Duplicated tuple will be ignored.
                        freshman = Members(memberId = newUser[keys['memberId']],
                                           password = newUser[keys['memberId']],
                                           memberName = newUser[keys['memberName']],
                                           authority = newUser[keys['authority']],
                                           signedInDate = datetime.now())
                        dao.add(freshman)
                        dao.commit()
                    except:
                        dao.rollback()
                        error = 'Error has been occurred while adding new users'
                        return render_template('/class_add_user.html',
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               ownCourses = ownCourses,
                                               allUsers = allUsers,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments,
                                               authorities = authorities,
                                               newUsers = newUsers)
                        
                isExist = dao.query(Registrations).\
                              filter(and_(Registrations.memberId == newUser[keys['memberId']],
                                          Registrations.courseId == newUser[keys['courseId']].split()[0])).\
                              first()
                # new member
                if not isExist:
                    try:
                        # then insert to 'Registrations'.
                        freshman = Registrations(memberId = newUser[keys['memberId']],
                                                 courseId = newUser[keys['courseId']].split()[0])
                        dao.add(freshman)
                        dao.commit()
                    except:
                        dao.rollback()
                        error = 'Error has been occurred while registering new users'
                        return render_template('/class_add_user.html',
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               ownCourses = ownCourses,
                                               allUsers = allUsers,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments,
                                               authorities = authorities,
                                               newUsers = newUsers)
                    
                    try:
                        departmentInformation = DepartmentsDetailsOfMembers(memberId = newUser[keys['memberId']],
                                                                            collegeIndex = newUser[keys['collegeIndex']],
                                                                            departmentIndex = newUser[keys['departmentIndex']])
                        dao.add(departmentInformation)
                        dao.commit()
                    except:
                        dao.rollback()
                # old member
                else:
                    # suppose the user's department is different with his registered information
                    try:
                        departmentInformation = DepartmentsDetailsOfMembers(memberId = newUser[keys['memberId']],
                                                                            collegeIndex = newUser[keys['collegeIndex']],
                                                                            departmentIndex = newUser[keys['departmentIndex']])
                        dao.add(departmentInformation)
                        dao.commit()
                    except:
                        dao.rollback()
                        
                courseName = dao.query(RegisteredCourses).\
                                 filter(RegisteredCourses.courseId == newUser[keys['courseId']].split()[0]).\
                                 first().\
                                 courseName

                memberPath = '%s/%s/%s_%s/%s_%s' % (projectPath,
                                                    coursesPath,
                                                    newUser[keys['courseId']].split()[0],
                                                    courseName.replace(' ', ''),
                                                    newUser[keys['memberId']],
                                                    newUser[keys['memberName']].replace(' ', ''))
                
                if not os.path.exists(memberPath):
                    os.makedirs(memberPath)
                
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
                    if targetUser == newUser[keys['memberId']]:
                        del newUsers[index]
                        break
                    index += 1
    
    return render_template('/class_add_user.html',
                           error = error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           ownCourses = ownCourses,
                           allUsers = allUsers,
                           allColleges = allColleges,
                           allDepartments = allDepartments,
                           authorities = authorities,
                           newUsers = newUsers)

@GradeServer.route('/classmaster/user_submit/summary')
@login_required
def user_submit_summary():
    # moved from URL, error will occur
    if request.referrer.rsplit('/', 1)[1] != "user_submit/summary":
        error = "invalid access"
        print error
        
    error = None

    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID]).\
                         all()
    except:
        return render_template('/class_user_submit_summary.html',
                               error=error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               ownCourses=[],
                               ownProblems=[],
                               ownMembers=[],
                               submissions=[])
    try:       
        ownProblems = dao.query(RegisteredProblems).\
                          join(RegisteredCourses,
                               RegisteredProblems.courseId == RegisteredCourses.courseId).\
                          filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID]).\
                          all()
    except:
        return render_template('/class_user_submit_summary.html',
                               error=error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               ownCourses=ownCourses,
                               ownProblems=[],
                               ownMembers=[],
                               submissions=[])     
    try:                 
        ownMembers = dao.query(Registrations).\
                         join(RegisteredCourses,
                              RegisteredCourses.courseId == Registrations.courseId).\
                         filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID]).\
                         all()
    except:
        return render_template('/class_user_submit_summary.html',
                               error=error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               ownCourses=ownCourses,
                               ownProblems=ownProblems,
                               ownMembers=[],
                               submissions=[])                     
    try:
        submissions = dao.query(Submissions.memberId,Submissions.courseId,Submissions.problemId,func.max(Submissions.submissionCount).label("maxSubmissionCount")).\
                      group_by(Submissions.memberId,Submissions.courseId,Submissions.problemId).\
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
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           ownCourses=ownCourses,
                           ownProblems=ownProblems,
                           ownMembers=ownMembers,
                           submissions=latestSubmissions)

@GradeServer.route('/classmaster/manage_service')
@login_required
def class_manage_service():
    # moved from URL, error will occur
    if request.referrer.rsplit('/', 1)[1] != "manage_service":
        error = "invalid access"
        print error
        
    # To do
    error = None
    return render_template('/class_manage_service.html',
                           error = error,
                           SETResources = SETResources,
                           SessionResources = SessionResources,)
