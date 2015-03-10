# -*- coding: utf-8 -*-
"""
    GradeSever.controller.login
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    로그인 확인 데코레이터와 로그인 처리 모듈.

    :copyright: (c) 2015 by KookminUniv

"""

from flask import request, render_template, url_for, redirect, session
from sqlalchemy import func
from datetime import datetime

from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils import login_required

from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.languages import Languages
from GradeServer.model.languagesOfCourses import LanguagesOfCourses
from GradeServer.model.members import Members
from GradeServer.model.colleges import Colleges
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.departments import Departments
from GradeServer.model.courses import Courses
from GradeServer.model.problems import Problems

import re
import zipfile
import os
import shutil

newUsers = []

@GradeServer.route('/master/<memberId>')
@login_required
def server_master_signin(memberId):
    return render_template('/server_master_signin.html')

@GradeServer.route('/master/manage_problem', methods=['GET', 'POST'])
@login_required
def server_manage_problem():
    if request.method == 'POST':
        for form in request.form:
            if form == 'upload':
                files = request.files.getlist("files")
                if not list(files)[0].filename:
                    break
                
                nextIndex = 0
                try:
                    nextIndex = dao.query(Problems).count()
                except:
                    nextIndex = 0
                    
                # if there's additional difficulty then change the value 'numberOfDifficulty'
                numberOfDifficulty = 5
                
                numberOfProblemsOfDifficulty = [0]*numberOfDifficulty
                for difficulty in range(0, numberOfDifficulty):
                    difficultyOfProblem = str(difficulty+1)
                    numberOfProblemsOfDifficulty[difficulty] = dao.query(Problems.problemId)\
                                                                .filter(Problems.problemId.like(difficultyOfProblem+"%"))\
                                                                .count()
                
                # read each uploaded file(zip)
                for fileData in files:
                    # unzip each file
                    tmpPath = "/mnt/shared/tmp"
                    with zipfile.ZipFile(fileData, "r") as z:
                        z.extractall(tmpPath)
                    
                    problemName = os.listdir(tmpPath)[0]
                    problemInformation = open(tmpPath+"/"+problemName+"/"+problemName+".txt", "r").read()
                    
                    nextIndex = nextIndex+1
                    # slice and make information from 'key=value, key=value, ...'
                    problemInformation = problemInformation.split(', ') 
                    difficulty = solutionCheckType = limitedTime = limitedMemory = 0
                    
                    problemPath = "/mnt/shared/Problems/"
                    
                    # reslice and make information from 'key=value'
                    for eachInformation in problemInformation:
                        key = eachInformation.split('=')[0]
                        value = eachInformation.split('=')[1]
                        if key == 'Name':
                            problemName = value
                        elif key == 'Difficulty':
                            difficulty = int(value)
                        elif key == 'SolutionCheckType':
                            solutionCheckType = value
                        elif key == 'LimitedTime':
                            limitedTime = int(value)
                        elif key == 'LimitedMemory':
                            limitedMemory = int(value)
                            
                    numberOfProblemsOfDifficulty[difficulty-1]+=1
                    # place the difficulty at the left most
                    
                    problemId = difficulty*10000+numberOfProblemsOfDifficulty[difficulty-1]
                    problemPath += str(problemId)+"_"+problemName
                    newProblem = Problems(problemIndex=nextIndex, problemId=problemId, problemName=problemName, solutionCheckType=solutionCheckType, limitedTime=limitedTime,\
                                          limitedMemory=limitedMemory, problemPath=problemPath)
                    
                    dao.add(newProblem)
                    dao.commit()
                    
                    # rename new problem folder
                    os.chdir("%s/%s/%s_%s" % (tmpPath, problemName, problemName, solutionCheckType))
                    os.system("rename 's/\.*/%s_/' *" % (problemId))
                    # change problems information files name
                    os.chdir("%s/%s" % (tmpPath, problemName))
                    os.system("rename 's/\.*/%s_/' *" % (problemId))
                    # change problem folder name
                    os.chdir("%s" % tmpPath)
                    os.system("rename 's/\.*/%s_/' *" % (problemId))
                    
                    # after all, move the problem into 'Problems' folder
                    shutil.move(tmpPath, problemPath)
                    
            else:
                dao.query(Problems).filter_by(problemId=int(form)).update(dict(isDeleted='Deleted'))
                dao.commit()

        return redirect(url_for('.server_manage_problem'))
        
    else:
        uploadedProblems = []
        try:
            uploadedProblems = dao.query(Problems).filter(Problems.isDeleted=='Not-Deleted').all()
        except:
            uploadedProblems = []
        return render_template('/server_manage_problem.html', uploadedProblems=uploadedProblems)

@GradeServer.route('/master/manage_class', methods=['GET', 'POST'])
@login_required
def server_manage_class():
    error = None
    try:
        courses = dao.query(RegisteredCourses).order_by(RegisteredCourses.endDateOfCourse.desc()).all()
        languagesOfCourse = dao.query(LanguagesOfCourses.courseId, LanguagesOfCourses.languageIndex, LanguagesOfCourses.languageVersion, \
                                    Languages.languageName.label("languageName")).\
                                    join(Languages, LanguagesOfCourses.languageIndex==Languages.languageIndex).all()
    except:
        print "Empty 'RegisteredCoruses' table"
            
    if request.method == 'POST':
        for form in request.form:
            try:
                deleteTarget = dao.query(RegisteredCourses).filter_by(courseId=form).first()
                dao.delete(deleteTarget)
                try:
                    dao.commit()
                except:
                    error = "Cannot delete"
            except:
                print "Deletion Error"
                
        return redirect(url_for('.server_manage_class'))
    
    session['ownCourses'] = dao.query(RegisteredCourses).all()
    
    return render_template('/server_manage_class.html', error=error, courses=courses, languagesOfCourse=languagesOfCourse)

@GradeServer.route('/master/manage_users', methods=['GET', 'POST'])
@login_required
def server_manage_user():
    try:
        users = dao.query(Members.memberId, Members.memberName, Members.contactNumber, Members.emailAddress, Members.authority, Members.lastAccessDate, Departments.departmentName).\
                    join(DepartmentsDetailsOfMembers, Members.memberId==DepartmentsDetailsOfMembers.memberId).\
                    join(Departments, Departments.departmentIndex==DepartmentsDetailsOfMembers.departmentIndex).\
                    order_by(Members.signedInDate.desc()).all()
                          
    except Exception as e:
        Log.error(e)
        raise e
              
    if request.method=='POST':
        for form in request.form:
            try:
                deleteTarget = dao.query(Members).filter_by(memberId=form).first()
                dao.delete(deleteTarget)
                dao.commit()
                
            except Exception as e:
                Log.error(e)
                raise e
        return redirect(url_for('.server_manage_user'))
    
    index = len(users)
    return render_template('/server_manage_user.html', users=users, index=index)

@GradeServer.route('/master/manage_service')
@login_required
def server_manage_service():
    return render_template('/server_manage_service.html')

@GradeServer.route('/master/add_class', methods=['GET', 'POST'])
@login_required
def server_add_class():
    error = None
    
    allCourses = dao.query(Courses).all()
    allLanguages = dao.query(Languages).all()
    if request.method=='POST':
        courseAdministratorId = request.form['courseAdministratorId']
        semester = request.form['semester']
        courseDescription = request.form['courseDescription']
        startDateOfCourse = request.form['startDateOfCourse']
        endDateOfCourse = request.form['endDateOfCourse']
        courseIndex = request.form['courseId'].split(' ')[0]
        courseName = request.form['courseId'][len(courseIndex)+1:]
        languages = []
        for form in request.form:
            if "languageIndex" in form:
                languages.append(request.form[form].split('_'))
                
        if not courseIndex:
            error = "You have to choose a class name"
        elif not courseAdministratorId:
            error = "You have to enter a manager Id"
        elif not semester:
            error = "You have to enter a manager Id"
        elif not languages:
            error = "You have to choose at least one language"
        elif not courseDescription:
            error = "You have to enter a class description"
        elif not startDateOfCourse:
            error = "You have to choose a start date"
        elif not endDateOfCourse:
            error = "You have to choose a end date"
        else:
            existCoursesNum = dao.query(RegisteredCourses.courseId).all()
            print "exist", existCoursesNum
            print startDateOfCourse[:4], semester, int(courseIndex)
            newCourseNum = "%s%s%03d"%(startDateOfCourse[:4], semester, int(courseIndex)) # yyyys
            print "new", newCourseNum
            checker = 1
            for existCourse in existCoursesNum:
                print "33"
                # if the course is already registered, then make another subclass
                if existCourse[0][:8]==newCourseNum:
                    print existCourse[0][:8]
                    print "in"
                    
                    currentSubCourseNum = dao.query(func.count(RegisteredCourses.courseId).label("num")).filter(RegisteredCourses.courseId.like(newCourseNum+"__")).first().num
                    print "count:",currentSubCourseNum
                    """
                    수정할것!!count 사용해서
                    func.count().label
                    """
                    newCourseNum = "%s%02d"%(existCourse[0][:8], currentSubCourseNum+1) # yyyysccc
                    print newCourseNum
                    checker = 0
                    break
                
            # new class case
            if checker:
                newCourseNum = "%s01"%(newCourseNum)
            
            newCourse = RegisteredCourses(courseId=newCourseNum, courseName=courseName, courseDescription=courseDescription, \
                               startDateOfCourse=startDateOfCourse, endDateOfCourse=endDateOfCourse, courseAdministratorId=courseAdministratorId)    
            dao.add(newCourse)
            dao.commit()
            
            # create course folder in 'CurrentCourses' folder
            problemPath = "/mnt/shared/CurrentCourses/%s_%s" %(newCourseNum, courseName)
            print problemPath
            if not os.path.exists(problemPath):
                os.makedirs(problemPath)
            
            for language in languages:
                languageIndex, languageVersion = language
                print languageIndex, languageVersion
                newCourseLanguage = LanguagesOfCourses(courseId=newCourseNum, languageIndex=int(languageIndex), languageVersion=languageVersion)
                dao.add(newCourseLanguage)
                dao.commit()
            
            return redirect(url_for('.server_manage_class'))
    
    return render_template('/server_add_class.html', error=error, courses=allCourses, languages=allLanguages)

@GradeServer.route('/master/addUser', methods=['GET', 'POST'])
@login_required
def server_add_user():
    global newUsers
    error = None
    targetUserIdToDelete = []
    if request.method == 'POST':
        for form in request.form:
            if form == 'addIndivisualUser':
                print "indivisual"
                
            elif form == 'addUserGroup':
                files = request.files.getlist("files")
                # if no file choosed
                if not list(files)[0].filename:
                    break
                # read each file
                for fileData in files:
                    # read each line    
                    for userData in fileData:
                        # slice and make information from 'key=value'
                        userInformation = userData.split(', ')
                        # userId, userName, authority, collegeIndex, collegeName, departmentIndex, departmentName
                        newUser = ['','','','','','','','']
                        
                        for eachData in userInformation:
                            if '=' in eachData:
                                # all authority is user in adding user from text file
                                newUser[2] = "User"
                                key = eachData.split('=')[0]
                                value = eachData.split('=')[1]
                                if key == "userId":
                                    for user in newUsers:
                                        if user[0] == value:
                                            #error = "There is a duplicated user id. Check the file and added user list"
                                            return redirect(url_for('.server_add_user'))
                                            
                                    newUser[0] = value 
                                elif key == "username":
                                    newUser[1] = value
                                elif key == "college":
                                    newUser[3] = value
                                    newUser[4] = dao.query(Colleges).filter_by(collegeIndex=value).first().collegeName
                                elif key == "department":
                                    newUser[5] = value
                                    newUser[6] = dao.query(Departments).filter_by(departmentIndex=value).first().departmentName
                                else:
                                    error = "Try again after check the manual"
                                    return render_template('/server_add_user.html', error=error, newUsers=newUsers)
                            else:
                                error = "Try again after check the manual"
                                return render_template('/server_add_user.html', error=error, newUsers=newUsers)
                            
                        newUsers.append(newUser)
            # after all, pushed 'Done' button
            elif form == 'addUser':
                for newUser in newUsers:
                    freshman = Members(memberId=newUser[0], password=newUser[0], memberName=newUser[1], authority=newUser[2], \
                                       signedInDate=datetime.now())
                    dao.add(freshman)
                    dao.commit()
                    
                    departmentInformation = DepartmentsDetailsOfMembers(memberId=newUser[0], collegeIndex=newUser[3], departmentIndex=newUser[5])
                    dao.add(departmentInformation)
                    dao.commit()
                    
                newUsers = [] # initialize add user list
                return redirect(url_for('.server_manage_user'))
            
            # pushed delete
            else:
                targetUserIdToDelete.append(form)
                
        # if id list is not empty
        if len(targetUserIdToDelete) != 0:
            # each target user id
            for targetUser in targetUserIdToDelete:
                index = 0
                print targetUser
                # each new user id
                for newUser in newUsers:
                    # if target id and new user id are same
                    if targetUser == newUser[0]:
                        del newUsers[index]
                        break
                    index+=1
                    
        return render_template('/server_add_user.html', error=error, newUsers=newUsers)
    else:
        
        return render_template('/server_add_user.html', error=error, newUsers=newUsers)
