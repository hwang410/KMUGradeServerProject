# -*- coding: utf-8 -*-
'''
    GradeSever.controller.classMaster
    
    Funcions for course administrator
    
    1. manage submissions of users
    2. manage problem
    3. manage user
    4. manage service

    :author: seulgi choi
    :copyright: (c) 2015 by Algorithmic Engineering Lab at KOOKMIN University
'''

from flask import request, render_template, url_for, redirect, session
from werkzeug.security import generate_password_hash

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.checkInvalidAccess import check_invalid_access

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
from sqlalchemy import and_,or_,func, exc
from datetime import datetime

from GradeServer.resource.setResources import SETResources
from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.languageResources import LanguageResources

import os
import re
import glob

projectPath = '/mnt/shared'
problemsPath = '%s/Problems' % projectPath
coursesPath = 'CurrentCourses'
limitedFileSize = 1024
DELETE = 'delete'
EDIT = 'edit'
TAB = 'Tab'
ADD = 'add'

newUsers = []
newProblems = []

def get_case_count(problemCasesPath, multipleFiles):
    caseCount = len(glob.glob(problemCasesPath+'/*'))/2
    
    if caseCount > 1:
        if multipleFiles == ENUMResources().const.FALSE:
            caseCount -= 1
        else:
            caseCount = 1
            
    return caseCount


def get_own_problems(memberId):
    try:
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
    except:
        ownProblems = []
    
    return ownProblems


def get_own_courses(memberId):
    try:
        ownCourses = dao.query(RegisteredCourses).\
                         filter(RegisteredCourses.courseAdministratorId == memberId).\
                         all()
    except:
        ownCourses = []
        
    return ownCourses


from GradeServer.py3Des.pyDes import *
def initialize_tripleDes_class():
    tripleDes = triple_des(OtherResources().const.TRIPLE_DES_KEY,
                           mode = ECB,
                           IV = '\0\0\0\0\0\0\0\0',
                           pad = None,
                           padmode = PAD_PKCS5)
    return tripleDes


def get_college_name(collegeIndex):
    error = None
    
    try:
        college_name = dao.query(Colleges).\
                           filter(Colleges.collegeIndex == collegeIndex).\
                           first().\
                           collegeName
    except:
        error = 'Error has been occurred while searching college name'
                   
    return error, college_name


def get_department_name(departmentIndex):
    error = None
    try:
        department_name = dao.query(Departments).\
                              filter(Departments.departmentIndex == departmentIndex).\
                              first().\
                              departmentName
    except:
        error = 'Error has been occurred while searching department name'
                      
    return error, department_name


'''
@ Get form value and set into array

keys : key dictionary which stores sort of keys
forms : request.form
array : 2-dimension array to store some information.
        array[index][form_name]
        'index' means each group of information(e.g. each user)
        'form_name' means each keys(e.g. userId, userName, and more)
'''
def set_form_value_into_array(keys, forms, array):
    error = None
    try:
        for form in forms:
            if form != 'addIndivisualUser':
                index, key_name, value = split_to_index_keyname_value(form)
                
                if key_name == 'userId':
                    array[index-1][keys['memberId']] = value
                elif key_name == 'username':
                    array[index-1][keys['memberName']] = value
                elif key_name == 'authority':
                    array[index-1][keys['authority']] = value
                elif key_name == 'college':
                    array[index-1][keys['collegeIndex']] = value.split()[0]
                    
                    # actually data.split()[1] is collegeName but it can be wrong, 
                    # so, here for checking the index is valid.
                    try:
                        error, array[index-1][keys['collegeName']] =\
                            get_college_name(array[index-1][keys['collegeIndex']])
                    except:
                        # Let this do 'pass' because after all this work,
                        # it checks all values are stored in the array
                        pass
                elif key_name == 'department':
                    array[index-1][keys['departmentIndex']] = value.split()[0]
                    
                    try:
                        error, array[index-1][keys['departmentName']] =\
                            get_department_name(array[index-1][keys['departmentIndex']])
                    except:
                        pass
                        
                elif key_name == 'courseId':
                    array[index-1][keys['courseId']] = value.strip()
                    
    except:
        error = 'Error has been occurred while inserting into temporary array from request form'

    return error, array


def set_array_from_csv_form(keys, csv_form, array):
    error = None
    try:        
        # 1. remove space and newline
        # 2. slice and make information from 'key=value'
        userInformation=\
            csv_form.replace(' ', '').replace('\n', '').replace('\r', '').\
            replace('\xef\xbb\xbf', '').split(',')
            
        for each_pair in userInformation:
            if '=' in each_pair:
                key, value = each_pair.split('=')
                
                if key == 'userId':
                    array[keys['memberId']] = value 
                elif key == 'username':
                    array[keys['memberName']] = value
                elif key == 'college':
                    array[keys['collegeIndex']] = value
                    error, array[keys['collegeName']] = get_college_name(value)
                    if error: pass
                elif key == 'department':
                    array[keys['departmentIndex']] = value
                    error, array[keys['departmentName']] = get_department_name(value)
                    if error: pass
                else:
                    error = 'Try again after check the manual'
                    break
                
            else:
                error = 'Try again after check the manual'
                break
    except:
        error = 'Error has been occurred while inserting into temporary array from csv form'
    
    return error, array
           
                
def set_array_from_file(files, keys, courseId):
    error = None
    try:
        if list(files)[0].filename:
            # read each file
            for fileData in files:
                # read each line    
                for userData in fileData:
                    newUser = [''] * 8
                    
                    error, newUser = set_array_from_csv_form(keys, userData, newUser)
                    
                    # Default authority of user group addition is 'User'
                    newUser[keys['authority']] = SETResources().const.USER
                    newUser[keys['courseId']] = courseId 
                    
                    if error:
                        return error
                    
                    # compares with all registered members
                    for user in newUsers:
                        if user[keys['memberId']] == newUser[keys['memberId']] and\
                           user[keys['collegeIndex']] == newUser[keys['collegeIndex']] and\
                           user[keys['departmentIndex']] == newUser[keys['departmentIndex']] and\
                           user[keys['courseId']] == newUser[keys['courseId']]:
                            error = 'There is a duplicated user ID. Check the file and added user list'
                            return error
                        
                    if check_validation(newUser):
                        newUsers.append(newUser)

    except:
        error = 'Error has been occurred while inserting values from user file'
    
    return error
        
                                        
def split_to_index_keyname_value(form):
    keyname,index = re.findall('\d+|\D+',form)
    return int(index), keyname, request.form[form]


def check_validation(user):
    isValid = True
    for key in user:
        if not key or key == '':
            isValid = False
            break
    
    return isValid
        
            
def get_own_members(memberId):
    error = None
    try:
        ownMembers = dao.query(Registrations).\
                     join(RegisteredCourses,
                          RegisteredCourses.courseId == Registrations.courseId).\
                     filter(RegisteredCourses.courseAdministratorId == session[memberId]).\
                     all()
    except:
        error = 'Error has been occurred while searching own members'
        
    return error, ownMembers


def get_all_problems():
    error = None
    
    try:
        allProblems = dao.query(Problems).\
                          filter(Problems.isDeleted == ENUMResources().const.FALSE).\
                          all()
    except:
        error = 'Error has been occurred while searching all problems'
        allProblems = []
        
    return error, allProblems


def delete_registered_problem(courseId, problemId):
    error = None
    
    targetProblem = dao.query(RegisteredProblems).\
                        filter(and_(RegisteredProblems.courseId == courseId,
                                    RegisteredProblems.problemId == problemId)).\
                        first()
    
    dao.delete(targetProblem)
        
    try:
        dao.commit()
    except exc.SQLAlchemyError:
        error = 'Error has been occurred while searching the problem to delete'
        
    return error
                
 
def update_registered_problem_info(courseId, problemId, key_dict):
    error = None
    
    dao.query(RegisteredProblems).\
        filter(and_(RegisteredProblems.courseId == courseId,
                    RegisteredProblems.problemId == problemId)).\
        update(key_dict)
    try:
        dao.commit()
    except exc.SQLAlchemyError:
        error = 'Error has been occurred while searching the problem to edit'
        
    return error
          
                        
def get_colleges():
    try:
        allColleges=dao.query(Colleges).\
                        filter(Colleges.isAbolished==\
                               SETResources().const.FALSE).\
                        all()
    except:
        allColleges=[]
        
    return allColleges

                                               
@GradeServer.route('/classmaster/user_submit')
@check_invalid_access
@login_required
def class_user_submit():
    error = None
    
    ownCourses = get_own_courses(session[SessionResources().const.MEMBER_ID])
            
    try:
        submissions = dao.query(Submissions.memberId,
                                Submissions.courseId,
                                Submissions.problemId,
                                func.max(Submissions.submissionCount).label('maxSubmissionCount')).\
                      group_by(Submissions.memberId,
                               Submissions.courseId,
                               Submissions.problemId).\
                      subquery()

        latestSubmissions = (dao.query(Submissions,
                                      RegisteredCourses,
                                      Problems).\
                                filter(Submissions.memberId == submissions.c.memberId,
                                       Submissions.courseId == submissions.c.courseId,
                                       Submissions.problemId == submissions.c.problemId,
                                       Submissions.submissionCount == submissions.c.maxSubmissionCount).\
                                join(RegisteredCourses,
                                     RegisteredCourses.courseId == Submissions.courseId).\
                                join(Problems,
                                     Problems.problemId == Submissions.problemId)).\
                            all()
                                
    except:
        error = 'Error has been occurred while searching submission records.'
        latestSubmissions = []
    
    return render_template('/class_user_submit.html',
                           error = error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           LanguageResources = LanguageResources,
                           ownCourses = ownCourses,
                           submissions = latestSubmissions)


@GradeServer.route('/classmaster/cm_manage_problem',methods=['GET','POST'])
@check_invalid_access
@login_required
def class_manage_problem():
    global projectPath
    global newProblems
    
    modalError = None

    error, allProblems = get_all_problems()
    if error:
        return render_template('/class_manage_problem.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               modalError = error,
                               allProblems = [],
                               ownCourses = [],
                               ownProblems = [])
    
    ownCourses = get_own_courses(session[SessionResources().const.MEMBER_ID])
    ownProblems = get_own_problems(session[SessionResources().const.MEMBER_ID])
        
    if request.method == 'POST':
        isNewProblem = True
        numberOfNewProblems = (len(request.form)-1)/7
        keys = {'courseId':0,
                'courseName':1,
                'problemId':2,
                'problemName':3,
                'isAllInputCaseInOneFile':4,
                'startDate':5,
                'endDate':6,
                'openDate':7,
                'closeDate':8}
        
        # courseId,courseName,problemId,problemName,isAllInputCaseInOneFile,startDate,endDate,openDate,closeDate
        newProblem = [['' for _ in range(len(keys.keys()))] for __ in range(numberOfNewProblems+1)]
        for form in request.form:
            if DELETE in form:
                isNewProblem = False
                courseId,problemId = form.split('_')[1:]
                if delete_registered_problem(courseId, problemId):
                    break
                                    
            elif EDIT in form:
                isNewProblem = False
                editTarget,courseId,problemId,targetData = form[5:].split('_')
                targetData = request.form[form]

                # actually editTarget is 'id' value of tag. 
                # That's why it may have 'Tab' at the last of id to clarify whether it's 'all' tab or any tab of each course.
                # so when user pushes one of tab and modify the data,then we need to re-make the editTarget 
                if TAB in editTarget:
                    editTarget = editTarget[:-3]
                for registeredProblem, registeredCourse, problemName in ownProblems:
                    if registeredCourse.courseId == courseId and\
                       registeredProblem.problemId == int(problemId):
                        kwargs = { editTarget : targetData }
                        if update_registered_problem_info(courseId, problemId, dict(**kwargs)):
                            break
                                                
            # addition problem
            else:
                value,index = re.findall('\d+|\D+',form)
                index = int(index)
                data = request.form[form]
                newProblem[index-1][keys[value]] = data
        
        if error:
            return render_template('/class_manage_problem.html',
                                   error = error, 
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
                                   LanguageResources = LanguageResources,
                                   modalError = modalError,
                                   allProblems = allProblems,
                                   ownCourses = ownCourses,
                                   ownProblems = ownProblems)
            
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
                        error = 'error has been occurred while getting solution check type'
                        return render_template('/class_manage_problem.html',
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               LanguageResources = LanguageResources,
                                               modalError = modalError,
                                               allProblems = allProblems,
                                               ownCourses = ownCourses,
                                               ownProblems = ownProblems)
                    
                    pathOfTestCase = '%s/%s_%s/%s_%s_%s' % (problemsPath,
                                                            problem[keys['problemId']],
                                                            problem[keys['problemName']],
                                                            problem[keys['problemId']],
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
                
                try:
                    dao.commit()
                except exc.SQLAlchemyError:
                    dao.rollback()
                    error = 'Error has been occurred while making a new problem'
                    return render_template('/class_manage_problem.html',
                                           error = error, 
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           LanguageResources = LanguageResources,
                                           modalError = modalError,
                                           allProblems = allProblems,
                                           ownCourses = ownCourses,
                                           ownProblems = ownProblems)

                
                newProblemRecord = SubmittedRecordsOfProblems(problemId = problem[keys['problemId']],
                                                              courseId = problem[keys['courseId']])
                dao.add(newProblemRecord)
                
                try:
                    dao.commit()
                except exc.SQLAlchemyError:
                    dao.rollback()
                    error = 'Error has been occurred while creating new record'
                    return render_template('/class_manage_problem.html',
                                           error = error, 
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           LanguageResources = LanguageResources,
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
                           LanguageResources = LanguageResources,
                           modalError = modalError,
                           allProblems = allProblems,
                           ownCourses = ownCourses,
                           ownProblems = ownProblems)


@GradeServer.route('/classmaster/cm_manage_user',methods=['GET','POST'])
@check_invalid_access
@login_required
def class_manage_user():
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
                               LanguageResources = LanguageResources,
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
                                   LanguageResources = LanguageResources,
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
    
    if request.method == 'POST':
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
                           LanguageResources = LanguageResources,
                           ownCourses=ownCourses,
                           ownUsers=ownUsersToData,
                           allUsers=allUsersToData,
                           colleges=colleges,
                           departments=departments)
    
    
@GradeServer.route('/classmaster/add_user',methods=['GET','POST'])
@check_invalid_access
@login_required
def class_add_user():
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
    
    ownCourses = get_own_courses(session[SessionResources().const.MEMBER_ID])

    if error:
        return render_template('/class_add_user.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               ownCourses = [],
                               allUsers = [],
                               allColleges = [],
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
        
    try:
        allUsers = (dao.query(Members,
                              Colleges,
                              Departments).\
                        join(DepartmentsDetailsOfMembers,
                             Members.memberId == DepartmentsDetailsOfMembers.memberId).\
                        join(Colleges,
                             DepartmentsDetailsOfMembers.collegeIndex == Colleges.collegeIndex).\
                        join(Departments,
                             DepartmentsDetailsOfMembers.departmentIndex == Departments.departmentIndex).\
                        filter(or_(Members.authority == SETResources().const.USER,
                                   Members.authority == SETResources().const.COURSE_ADMINISTRATOR)).\
                        group_by(Members.memberId)).\
                   all()
    except:
        error = 'Error has been occurred while searching all users'
        return render_template('/class_add_user.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               ownCourses = ownCourses,
                               allUsers = [],
                               allColleges = [],
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
    
    allColleges = get_colleges()
    
    
    try:
        allDepartments = (dao.query(DepartmentsOfColleges,
                                    Colleges,
                                    Departments).\
                              join(Colleges,
                                   Colleges.collegeIndex == DepartmentsOfColleges.collegeIndex).\
                              join(Departments,
                                   Departments.departmentIndex == DepartmentsOfColleges.departmentIndex).\
                              filter(Colleges.isAbolished == SETResources().const.FALSE).\
                              filter(Departments.isAbolished == SETResources().const.FALSE)).\
                         all()
    except:
        error = 'Error has been occurred while searching all departments'
        return render_template('/class_add_user.html',
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
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
            newUser = [['' for _ in range(len(keys.keys()))] for __ in range(numberOfUsers + 1)]
            
            error, newUser = set_form_value_into_array(keys, request.form, newUser)
                
            if error:
                return render_template('/class_add_user.html',
                                       error = error, 
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       LanguageResources = LanguageResources,
                                       ownCourses = ownCourses,
                                       allUsers = allUsers,
                                       allColleges = allColleges,
                                       allDepartments = allDepartments,
                                       authorities = authorities,
                                       newUsers = newUsers)
                            
            for index in range(numberOfUsers):
                if check_validation(newUser[index]):
                    newUsers.append(newUser[index])
                
        elif 'addUserGroup' in request.form:
            files = request.files.getlist('files')
            courseId = request.form['courseId'].split()[0]
            
            error = set_array_from_file(files, keys, courseId)
            
            if error:
                return render_template('/class_add_user.html',
                                       error = error, 
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       LanguageResources = LanguageResources,
                                       ownCourses = ownCourses,
                                       allUsers = allUsers,
                                       allColleges = allColleges,
                                       allDepartments = allDepartments,
                                       authorities = authorities,
                                       newUsers = newUsers)
                        
        elif 'addUser' in request.form:
            for newUser in newUsers:
                isExist = dao.query(Members).filter(Members.memberId == newUser[0]).first() 
                if not isExist:
                
                    if newUser[keys['authority']] == 'Course Admin':
                        newUser[keys['authority']] = SETResources().const.COURSE_ADMINISTRATOR
                            
                    tripleDes = initialize_tripleDes_class()
                    password = generate_password_hash(tripleDes.encrypt(str(newUser[keys['memberId']])))
                
                    # at first insert to 'Members'. Duplicated tuple will be ignored.
                    freshman = Members(memberId = newUser[keys['memberId']],
                                       password = password,
                                       memberName = newUser[keys['memberName']],
                                       authority = newUser[keys['authority']],
                                       signedInDate = datetime.now())
                    dao.add(freshman)
                    
                    try:
                        dao.commit()
                    except exc.SQLAlchemyError:
                        dao.rollback()
                        error = 'Error has been occurred while adding new users'
                        return render_template('/class_add_user.html',
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               LanguageResources = LanguageResources,
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
                    # then insert to 'Registrations'.
                    freshman = Registrations(memberId = newUser[keys['memberId']],
                                             courseId = newUser[keys['courseId']].split()[0])
                    dao.add(freshman)
                    
                    try:
                        dao.commit()
                    except exc.SQLAlchemyError:
                        dao.rollback()
                        error = 'Error has been occurred while registering new users'
                        return render_template('/class_add_user.html',
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               LanguageResources = LanguageResources,
                                               ownCourses = ownCourses,
                                               allUsers = allUsers,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments,
                                               authorities = authorities,
                                               newUsers = newUsers)
                    
                    
                    departmentInformation = DepartmentsDetailsOfMembers(memberId = newUser[keys['memberId']],
                                                                        collegeIndex = newUser[keys['collegeIndex']],
                                                                        departmentIndex = newUser[keys['departmentIndex']])
                    dao.add(departmentInformation)
                    
                    try:
                        dao.commit()
                    except exc.SQLAlchemyError:
                        dao.rollback()
                # old member
                else:
                    # suppose the user's department is different with his registered information    
                    departmentInformation = DepartmentsDetailsOfMembers(memberId = newUser[keys['memberId']],
                                                                        collegeIndex = newUser[keys['collegeIndex']],
                                                                        departmentIndex = newUser[keys['departmentIndex']])
                    dao.add(departmentInformation)
                    try:
                        dao.commit()
                    except exc.SQLAlchemyError:
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
                           LanguageResources = LanguageResources,
                           ownCourses = ownCourses,
                           allUsers = allUsers,
                           allColleges = allColleges,
                           allDepartments = allDepartments,
                           authorities = authorities,
                           newUsers = newUsers)


@GradeServer.route('/classmaster/user_submit/summary')
@check_invalid_access
@login_required
def user_submit_summary():
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
                               LanguageResources = LanguageResources,
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
                               LanguageResources = LanguageResources,
                               ownCourses=ownCourses,
                               ownProblems=[],
                               ownMembers=[],
                               submissions=[])     
    
    error, ownMembers = get_own_members(SessionResources().const.MEMBER_ID)

    if error:
        return render_template('/class_user_submit_summary.html',
                               error=error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               ownCourses=ownCourses,
                               ownProblems=ownProblems,
                               ownMembers=[],
                               submissions=[])                     
    try:
        submissions = dao.query(Submissions.memberId,
                                Submissions.courseId,
                                Submissions.problemId,
                                func.max(Submissions.submissionCount).label('maxSubmissionCount')).\
                      group_by(Submissions.memberId,
                               Submissions.courseId,
                               Submissions.problemId).\
                      subquery()

        latestSubmissions = dao.query(Submissions).\
                                filter(Submissions.memberId == submissions.c.memberId,
                                       Submissions.courseId == submissions.c.courseId,
                                       Submissions.problemId == submissions.c.problemId,
                                       Submissions.submissionCount == submissions.c.maxSubmissionCount).\
                                all()
    except:
        submissions = []
    
    return render_template('/class_user_submit_summary.html',
                           error=error,  
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           LanguageResources = LanguageResources,
                           ownCourses=ownCourses,
                           ownProblems=ownProblems,
                           ownMembers=ownMembers,
                           submissions=latestSubmissions)


@GradeServer.route('/classmaster/manage_service')
@check_invalid_access
@login_required
def class_manage_service():
    #TODO
    error = None
    
    return render_template('/class_manage_service.html',
                           error = error,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           LanguageResources = LanguageResources)
