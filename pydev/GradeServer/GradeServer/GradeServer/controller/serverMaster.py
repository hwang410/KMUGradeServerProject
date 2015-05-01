# -*- coding: utf-8 -*-
"""
    GradeSever.controller.login
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    로그인 확인 데코레이터와 로그인 처리 모듈.

    :copyright: (c) 2015 by KookminUniv

"""

from flask import request, render_template, url_for, redirect, session
from sqlalchemy import func, and_
from datetime import datetime

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.checkInvalidAccess import check_invalid_access

from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.languages import Languages
from GradeServer.model.languagesOfCourses import LanguagesOfCourses
from GradeServer.model.members import Members
from GradeServer.model.colleges import Colleges
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.departments import Departments
from GradeServer.model.courses import Courses
from GradeServer.model.departmentsOfColleges import DepartmentsOfColleges
from GradeServer.model.problems import Problems

from GradeServer.resource.setResources import SETResources
from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.sessionResources import SessionResources

import re
import zipfile
import os
import subprocess
import glob

projectPath = '/mnt/shared'
problemsPath = '%s/Problems' % (projectPath) # /mnt/shared/Problems
problemDescriptionsPath = '%s/pydev/GradeServer/GradeServer/GradeServer/static/ProblemDescriptions' % (projectPath)
# if there's additional difficulty then change the value 'numberOfDifficulty'
numberOfDifficulty = 5
newUsers = []
newColleges = []
newDepartments = []

currentTab = 'colleges'

@GradeServer.route('/master/manage_collegedepartment', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def server_manage_collegedepartment():
    global newColleges, newDepartments
    global currentTab
    # moved from other page, then show 'college' tab
    if request.referrer.rsplit('/', 1)[1] != "manage_collegedepartment":
        currentTab = 'colleges'
        
    error = None
    
    try:
        allColleges = dao.query(Colleges).\
                          all()
    except:
        error = 'Error has been occurred while searching colleges'
        return render_template('/server_manage_collegedepartment.html', 
                               error=error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               allColleges = [],
                               allDepartments = [])
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
        error = 'Error has been occurred while searching departments'
        return render_template('/server_manage_collegedepartment.html', 
                               error=error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               allColleges = allColleges,
                               allDepartments = [])
    
    if request.method == 'POST':
        isNewCollege = False
        isNewDepartment = False
        numberOfColleges = (len(request.form) - 1) / 2
        newCollege = [['' for i in range(2)] for j in range(numberOfColleges + 1)]
        numberOfDepartments = (len(request.form) - 1) / 3
        newDepartment = [['' for i in range(3)] for j in range(numberOfDepartments + 1)]
        for form in request.form:
            if 'addCollege' in request.form:
                isNewCollege = True
                if form != 'addCollege':
                    value, index = re.findall('\d+|\D+', form)
                    index = int(index)
                    data = request.form[form]
                    if value == 'collegeCode':
                        newCollege[index-1][0] = data
                    elif value == 'collegeName':
                        newCollege[index-1][1] = data
            elif 'addDepartment' in request.form:
                isNewDepartment = True
                if form != 'addDepartment':
                    value, index = re.findall('\d+|\D+', form)
                    index = int(index)
                    data = request.form[form]
                    if value == 'departmentCode':
                        newDepartment[index-1][0] = data
                    elif value == 'departmentName':
                        newDepartment[index-1][1] = data
                    elif value == 'collegeIndex':
                        newDepartment[index-1][2] = data.split()[0]
            elif 'deleteCollege' in request.form:
                if 'college' in form:
                    try:
                        collegeIndex = re.findall('\d+|\D+', form)[1]
                        target = dao.query(Colleges).filter(Colleges.collegeIndex == collegeIndex).first()
                        dao.delete(target)
                        dao.commit()
                    except:
                        error = 'Delete all departments before this work'
                        dao.rollback()
                        return render_template('/server_manage_collegedepartment.html', 
                                               error=error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments)
            elif 'deleteDepartment' in request.form:
                if 'department' in form:
                    try:
                        departmentIndex = re.findall('\d+|\D+', form)[1]
                        target = dao.query(DepartmentsOfColleges).filter(DepartmentsOfColleges.departmentIndex == departmentIndex).first()
                        dao.delete(target)
                        dao.commit()
                        target = dao.query(Departments).filter(Departments.departmentIndex == departmentIndex).first()
                        dao.delete(target)
                        dao.commit()
                    except:
                        error = 'Error has been occurred while searching departments'
                        dao.rollback()
                        return render_template('/server_manage_collegedepartment.html', 
                                               error=error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments)
        
                
        if isNewCollege:
            for index in range(numberOfColleges):
                newColleges.append(newCollege[index])
            for newPart in newColleges:
                if newPart[1]:
                    try:
                        newCollege = Colleges(collegeCode = newPart[0],
                                              collegeName = newPart[1])
                        dao.add(newCollege)
                        dao.commit()
                    except:
                        error = 'Error has been occurred while making new college'
                        dao.rollback()
                        return render_template('/server_manage_collegedepartment.html', 
                                               error=error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments)
            newColleges = []
            currentTab = 'colleges'
            
        if isNewDepartment:
            for index in range(numberOfDepartments):
                newDepartments.append(newDepartment[index])
            newDepartment = []
            for newPart in newDepartments:
                if newPart[1]:
                    try:
                        newDepartment = Departments(departmentCode = newPart[0],
                                                    departmentName = newPart[1])
                        dao.add(newDepartment)
                        dao.commit()
                    except:
                        error = 'Error has been occurred while making new department'
                        dao.rollback()
                        return render_template('/server_manage_collegedepartment.html', 
                                               error=error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments)
                    try:
                        index = dao.query(func.max(Departments.departmentIndex)).scalar()
                        relationToCollege = DepartmentsOfColleges(collegeIndex = newPart[2],
                                                                  departmentIndex = index)
                        dao.add(relationToCollege)
                        dao.commit()
                    except:
                        error = 'Error has been occurred while making new relation of department'  
                        dao.rollback()
                        return render_template('/server_manage_collegedepartment.html', 
                                               error=error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments)
                        
            newDepartments = []
            currentTab = 'departments'
            
        return redirect(url_for('.server_manage_collegedepartment'))
    return render_template('/server_manage_collegedepartment.html', 
                           error=error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           currentTab = currentTab,
                           allColleges = allColleges,
                           allDepartments = allDepartments)
        
@GradeServer.route('/master/manage_class', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def server_manage_class():
        
    error = None
    
    try:
        courses = (dao.query(RegisteredCourses,
                             Members).\
                       join(Members,
                            Members.memberId == RegisteredCourses.courseAdministratorId).\
                       order_by(RegisteredCourses.endDateOfCourse.desc())).\
                  all()
    except:
        courses = []
        #error = 'No courses exists'
        
    try:
        languagesOfCourse = dao.query(LanguagesOfCourses.courseId, 
                                      Languages.languageIndex,
                                      Languages.languageName).\
                                 join(Languages,
                                      LanguagesOfCourses.languageIndex == Languages.languageIndex).\
                            all()
    except:
        languagesOfCourse = []
        #error = 'No information of languages of courses'

    if request.method == 'POST':
        for form in request.form:
            try:
                deleteTarget = dao.query(RegisteredCourses).\
                                   filter(RegisteredCourses.courseId == form).\
                                   first()
                dao.delete(deleteTarget)
                dao.commit()
            except:
                dao.rollback()
                print 'Deletion Error'
                
        return redirect(url_for('.server_manage_class'))
    
    session['ownCourses'] = dao.query(RegisteredCourses).all()
    
    return render_template('/server_manage_class.html',
                           error = error,  
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           courses = courses, 
                           languagesOfCourse = languagesOfCourse)
    
@GradeServer.route('/master/add_class', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def server_add_class():
    global projectPath
    error = None
    courseAdministrator = ''
    semester = 1
    courseDescription = ''
    startDateOfCourse = ''
    endDateOfCourse = ''
    courseIndex = ''
    courseName = ''
    languages = []
    
    try:
        allCourses = dao.query(Courses).\
                         all()
    except:
        error = 'Error has been occurred while searching courses'
    
    try:
        allLanguages = dao.query(Languages).\
                           all()
    except:
        error = 'Error has been occurred while searching languages'
    
    try:               
        allCourseAdministrators = dao.query(Members).\
                                      filter(Members.authority==SETResources().const.COURSE_ADMINISTRATOR).\
                                      all()
    except:
        error = 'Error has been occurred while searching course administrators'
                        
    if request.method == 'POST':
        courseAdministrator = request.form['courseAdministrator']
        semester = request.form['semester'] 
        courseDescription = request.form['courseDescription']
        startDateOfCourse = request.form['startDateOfCourse']
        endDateOfCourse = request.form['endDateOfCourse']
        courseIndex, courseName = request.form['courseId'].split(' ', 1)
        
        for form in request.form:
            if 'languageIndex' in form:
                languages.append(request.form[form].split('_'))
                
        if not courseIndex:
            error = 'You have to choose a class name'
        elif not courseAdministrator:
            error = 'You have to enter a manager'
        elif not semester:
            error = 'You have to choose a semester'
        elif not languages:
            error = 'You have to choose at least one language'
        elif not courseDescription:
            error = 'You have to enter a class description'
        elif not startDateOfCourse:
            error = 'You have to choose a start date'
        elif not endDateOfCourse:
            error = 'You have to choose a end date'
        else:
            startDate = datetime.strptime(startDateOfCourse, "%Y-%m-%d").date()
            endDate = datetime.strptime(endDateOfCourse, "%Y-%m-%d").date()
            if startDate > endDate:
                error = "Start date should be earlier than end date"
                return render_template('/server_add_class.html', 
                                       error = error, 
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       courseAdministrator = courseAdministrator,
                                       semester = semester,
                                       courseDescription = courseDescription,
                                       startDateOfCourse = "",
                                       endDateOfCourse = "",
                                       courseIndex = courseIndex,
                                       courseName = courseName,
                                       choosedLanguages = languages,
                                       courses = allCourses, 
                                       languages = allLanguages,
                                       allCourseAdministrators = allCourseAdministrators)
            
            try:
                dao.query(Members).\
                    filter(and_(Members.authority == SETResources().const.COURSE_ADMINISTRATOR,
                                Members.memberId == courseAdministrator.split()[0])).\
                    first().memberId
            except:
                error = "%s is not registered as a course administrator" % (courseAdministrator.split()[0])
                return render_template('/server_add_class.html', 
                                       error = error, 
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       courseAdministrator = courseAdministrator,
                                       semester = semester,
                                       courseDescription = courseDescription,
                                       startDateOfCourse = startDateOfCourse,
                                       endDateOfCourse = endDateOfCourse,
                                       courseIndex = courseIndex,
                                       courseName = courseName,
                                       choosedLanguages = languages,
                                       courses = allCourses, 
                                       languages = allLanguages,
                                       allCourseAdministrators = allCourseAdministrators)

            existCoursesNum = dao.query(RegisteredCourses.courseId).\
                                  all()
            newCourseNum = '%s%s%03d' % (startDateOfCourse[:4], semester, int(courseIndex)) # yyyys
            isNewCourse = True
            for existCourse in existCoursesNum:
                # if the course is already registered, then make another subclass
                if existCourse[0][:8] == newCourseNum:
                    NumberOfCurrentSubCourse = dao.query(func.count(RegisteredCourses.courseId).label('num')).\
                                                   filter(RegisteredCourses.courseId.like(newCourseNum+'__')).\
                                                   first().\
                                                   num
                    """
                    수정할것!!count 사용해서
                    func.count().label
                    """
                    newCourseNum = '%s%02d' % (existCourse[0][:8], 
                                               NumberOfCurrentSubCourse + 1) # yyyysccc
                    isNewCourse = False
                    break
            # new class case
            if isNewCourse:
                newCourseNum = '%s01' % (newCourseNum)
            try:
                newCourse = RegisteredCourses(courseId = newCourseNum, 
                                              courseName = courseName, 
                                              courseDescription = courseDescription,
                                              startDateOfCourse = startDateOfCourse, 
                                              endDateOfCourse = endDateOfCourse, 
                                              courseAdministratorId = courseAdministrator.split(' ')[0])    
                dao.add(newCourse)
                dao.commit()
            except:
                dao.rollback()
                error = 'Creation course failed'
                return render_template('/server_add_class.html', 
                                       error = error, 
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       courses = allCourses, 
                                       languages = allLanguages)
            
            # create course folder in 'CurrentCourses' folder
            courseName = courseName.replace(' ', '')
            problemPath = "%s/CurrentCourses/%s_%s" % (projectPath, newCourseNum, courseName)
            if not os.path.exists(problemPath):
                os.makedirs(problemPath)
            for language in languages:
                languageIndex, languageVersion = language
                try:
                    newCourseLanguage = LanguagesOfCourses(courseId = newCourseNum, 
                                                           languageIndex = int(languageIndex))
                    dao.add(newCourseLanguage)
                    dao.commit()
                except:
                    dao.rollback()
                    error = 'Course language error'
                    return render_template('/server_add_class.html', 
                                           error = error, 
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           courses = allCourses, 
                                           languages = allLanguages)
            return redirect(url_for('.server_manage_class'))

    return render_template('/server_add_class.html', 
                           error = error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           courseAdministrator = courseAdministrator,
                           semester = semester,
                           courseDescription = courseDescription,
                           startDateOfCourse = startDateOfCourse,
                           endDateOfCourse = endDateOfCourse,
                           courseIndex = courseIndex,
                           courseName = courseName,
                           choosedLanguages = languages,
                           courses = allCourses, 
                           languages = allLanguages,
                           allCourseAdministrators = allCourseAdministrators)
    
@GradeServer.route('/master/manage_problem', methods=['GET', 'POST'])
@check_invalid_access
@login_required
def server_manage_problem():
    global projectPath
    global numberOfDifficulty
    error = None
    
    if request.method == 'POST':
        for form in request.form:
            if form == 'upload':
                files = request.files.getlist("files")
                if not list(files)[0].filename:
                    error = 'Uploading file error'
                    break
                
                try:
                    nextIndex = dao.query(Problems).\
                                    count()
                except:
                    nextIndex = 0

                numberOfProblemsOfDifficulty = [0] * numberOfDifficulty
                
                for difficulty in range(numberOfDifficulty):
                    difficultyOfProblem = str(difficulty + 1)
                    try:
                        numberOfProblemsOfDifficulty[difficulty] = dao.query(Problems.problemId).\
                                                                       filter(Problems.problemId.like(difficultyOfProblem + '%')).\
                                                                       count()
                    except:
                        error = 'Error has occurred while searching problems'
                        return render_template('/server_manage_problem.html', 
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               uploadedProblems = [])
                # read each uploaded file(zip)
                for fileData in files:
                    tmpPath = '%s/tmp' % projectPath
                    # if 'tmp' folder exists, there had an error before while uploading a problem.
                    # so, check and delete before unzip
                    if os.path.exists(tmpPath):
                        try:
                            subprocess.call('rm -rf %s' % tmpPath, shell=True)
                        except OSError:
                            error = 'Cannot delete \'tmp\' folder'
                            return render_template('/server_manage_problem.html', 
                                                   error = error, 
                                                   SETResources = SETResources,
                                                   SessionResources = SessionResources,
                                                   uploadedProblems = [])
                            
                    # unzip file
                    with zipfile.ZipFile(fileData, 'r') as z:
                        z.extractall(tmpPath)
                    
                    # splitting by .(dot) or _(under bar)
                    # if the problem zip's made on window environment, problem name's broken.
                    # so it needs to be decoded.
                    rowProblemName = re.split('_|\.', os.listdir(tmpPath)[0])[0]
                    problemName = str(rowProblemName.decode('cp949'))

                    byteString = '?'*len(rowProblemName)
                    
                    os.chdir('%s' % tmpPath)
                    
                    # rename text file
                    subprocess.call('mv %s.txt %s.txt' % (byteString, problemName), shell=True)
                    
                    # rename pdf file
                    subprocess.call('mv %s.pdf %s.pdf' % (byteString, problemName), shell=True)
                    
                    # rename folders
                    # checking for both check type because we can't check the type.
                    subprocess.call('mv %s_SOLUTION %s_SOLUTION' % (byteString, problemName), shell=True)
                    subprocess.call('mv %s_CHECKER %s_CHECKER' % (byteString, problemName), shell=True)
                    
                    problemInformationPath = '%s/%s.txt' % (tmpPath, problemName)
                    problemInformation = open(problemInformationPath, 'r').read()
                    problemInformation = problemInformation.decode('cp949')
                    
                    nextIndex += 1
                    # slice and make information from 'key=value, key=value, ...'
                    problemInformation = problemInformation.split(', ')

                    difficulty = 0
                    solutionCheckType = 0
                    limitedTime = 0
                    limitedMemory = 0

                    # reslice and make information from 'key=value'
                    for eachInformation in problemInformation:
                        key, value = eachInformation.split('=')
                        if key == 'Name':
                            problemName = value
                        elif key == 'Difficulty':
                            difficulty = int(value)
                        elif key == 'SolutionCheckType':
                            solutionCheckType = ENUMResources().const.SOLUTION if value == "Solution" else ENUMResources().const.CHECKER
                        elif key == 'LimitedTime':
                            limitedTime = int(value)
                        elif key == 'LimitedMemory':
                            limitedMemory = int(value)
                    numberOfProblemsOfDifficulty[difficulty - 1] += 1
                             
                    # place the difficulty at the left most
                    problemId = difficulty * 10000 + numberOfProblemsOfDifficulty[difficulty - 1]
                    problemPath = '%s/%s' % (problemsPath,
                                             str(problemId) + '_' + problemName.replace(' ', ''))
                    
                    try:
                        newProblem = Problems(problemIndex = nextIndex, 
                                              problemId = problemId, 
                                              problemName = problemName, 
                                              solutionCheckType = solutionCheckType, 
                                              limitedTime = limitedTime,
                                              limitedMemory = limitedMemory, 
                                              problemPath = problemPath)
                        dao.add(newProblem)
                        dao.commit()
                    except:
                        dao.rollback()
                        error = 'Creation Problem Error'
                        return render_template('/server_manage_problem.html', 
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               uploadedProblems = [])
                    
                    # rename new problem folder
                    os.chdir('%s/%s_%s' % (tmpPath, 
                                           problemName, 
                                           solutionCheckType))
                    # current path : ../tmp/problemName_solutionCheckType
                    
                    inOutCases = [file for file in os.listdir(os.getcwd())]
                    
                    for file in inOutCases:
                        rowFileName = file
                        fileName = '%s_%s' % (problemName, rowFileName.split('_', 1)[1])
                        subprocess.call('mv %s %s' % (rowFileName, str(fileName)), shell=True)
                        
                    # remove space on file/directory names
                    try:
                        subprocess.call('for f in *; do mv "$f" `echo $f|sed "s/ //g"`;done', shell=True)
                    except OSError:
                        error = 'Error has occurred while removing space of folder name'
                        return render_template('/server_manage_problem.html', 
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               uploadedProblems = [])
                    
                    # put problemId ahead
                    try:
                        subprocess.call('for f in *; do mv $f `echo $f|sed "s/\.*/%s_/"`;done' % (problemId), shell=True)
                    except OSError:
                        error = 'Error has occurred while renaming a folder'
                        return render_template('/server_manage_problem.html', 
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               uploadedProblems = [])
                        
                    problemName = problemName.replace(' ', '')
                    
                    os.chdir('%s' % (tmpPath))
                    # current path : ../tmp
                   
                    # remove space on file/directory names
                    try:
                        subprocess.call('for f in *; do mv "$f" `echo $f|sed "s/ //g"`;done', shell=True)
                    except OSError:
                        error = 'Error has occurred while removing space of folder name'
                        return render_template('/server_manage_problem.html', 
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               uploadedProblems = [])
                    
                    try:
                        subprocess.call('for f in *; do mv $f `echo $f|sed "s/\.*/%s_/"`;done' % (problemId), shell=True)
                    except OSError:
                        error = 'Error has occurred while renaming a folder'
                        return render_template('/server_manage_problem.html', 
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               uploadedProblems = [])
                        
                    # create final goal path
                    if not os.path.exists(problemPath):
                        os.makedirs(problemPath)
                    
                    problemName = problemName.replace(' ', '')
                    problemDescriptionPath = '%s/%s_%s' % (problemDescriptionsPath, problemId, problemName)
                    if not os.path.exists(problemDescriptionPath):
                        os.makedirs(problemDescriptionPath)

                    try:
                        # after all, move the problem into 'Problems' folder
                        subprocess.call('mv %s/* %s/' % (tmpPath, problemPath), shell=True)
                    except OSError :
                        error = 'Error has occurred while moving new problem'
                        return render_template('/server_manage_problem.html', 
                                               error = error, 
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               uploadedProblems = [])
                    
                    try:
                        subprocess.call('cp %s/%s_%s.pdf %s/' % (problemPath, problemId, problemName, problemDescriptionPath), shell=True)
                    except:
                        error = 'problem pdf doesn\'s exist'
                    
            else:
                try:
                    dao.query(Problems).\
                        filter(Problems.problemId == int(form)).\
                        update(dict(isDeleted = ENUMResources().const.TRUE))
                    dao.commit()
                except:
                    dao.rollback()
                    error = 'Problem deletion error'
                    return render_template('/server_manage_problem.html', 
                                           error = error, 
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           uploadedProblems = [])

        return redirect(url_for('.server_manage_problem'))
        
    else:
        try:
            uploadedProblems = dao.query(Problems).\
                                   filter(Problems.isDeleted == ENUMResources().const.FALSE).\
                                   all()
        except:
            uploadedProblems = []
            
    return render_template('/server_manage_problem.html', 
                           error = error, 
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           uploadedProblems = uploadedProblems)

@GradeServer.route('/master/manage_users', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def server_manage_user():
    error = None

    try:
        users = (dao.query(Members,
                           Colleges,
                           Departments).\
                     join(DepartmentsDetailsOfMembers, 
                          Members.memberId == DepartmentsDetailsOfMembers.memberId).\
                     join(Colleges,
                          Colleges.collegeIndex == DepartmentsDetailsOfMembers.collegeIndex).\
                     join(Departments, 
                          Departments.departmentIndex == DepartmentsDetailsOfMembers.departmentIndex).\
                     order_by(Members.memberId)).\
                all()
                
    except:
        error = 'Error has occurred while getting member information'
        return render_template('/server_manage_user.html', 
                               error = error, 
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               users = [], 
                               index = len(users))
    
    combineSameUsers = []
    userIndex = 1
    loopIndex = 0
    # if member in multiple department,
    # will be [member] [college] [department] [college] [department] ...
    for user, college, department in users:
        if loopIndex==0:
            combineSameUsers.append([user.memberId,
                                     user.memberName,
                                     user.contactNumber,
                                     user.emailAddress,
                                     user.authority,
                                     user.signedInDate,
                                     user.lastAccessDate,
                                     college.collegeName,
                                     department.departmentName])
        else:
            if user.memberId==combineSameUsers[userIndex-1][0]:
                combineSameUsers[userIndex-1].append(college.collegeName)
                combineSameUsers[userIndex-1].append(department.departmentName)
            else:
                combineSameUsers.append([user.memberId,
                                         user.memberName,
                                         user.contactNumber,
                                         user.emailAddress,
                                         user.authority,
                                         user.signedInDate,
                                         user.lastAccessDate,
                                         college.collegeName,
                                         department.departmentName])
                userIndex += 1
        loopIndex += 1
        
    if request.method == 'POST':
        for form in request.form:
            try:
                deleteTarget = dao.query(Members).\
                                   filter(Members.memberId == form).\
                                   first()
                dao.delete(deleteTarget)
                dao.commit()
                
            except:
                dao.rollback()
                error = 'Deletion error'
                return render_template('/server_manage_user.html', 
                                       error = error, 
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       users = combineSameUsers, 
                                       index = len(users))
                
        return redirect(url_for('.server_manage_user'))

    return render_template('/server_manage_user.html', 
                           error = error,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           users = combineSameUsers, 
                           index = len(users))



@GradeServer.route('/master/addUser', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def server_add_user():        
    global newUsers
    error = None
    targetUserIdToDelete = []
    authorities = ['Course Admin', 'User']
    try:
        allColleges = dao.query(Colleges).\
                          all()
    except:
        error = 'Error has been occurred while searching all colleges'
        return render_template('/server_add_user.html', 
                               error = error,  
                               SETResources = SETResources,
                               SessionResources = SessionResources,
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
        error = 'Error has been occurred while searching departments'
        return render_template('/class_add_user.html', 
                               error = error,  
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               allColleges = allColleges,
                               allDepartments = [],
                               authorities = authorities,
                               newUsers = newUsers)
        
    if request.method == 'POST':
        keys = {'memberId':0,
                'memberName':1,
                'authority':2,
                'collegeIndex':3,
                'collegeName':4,
                'departmentIndex':5,
                'departmentName':6}
        
        if 'addIndivisualUser' in request.form:
            # ( number of all form data - 'addIndivisualUser' form ) / forms for each person(id, name, college, department, authority)
            numberOfUsers = (len(request.form) - 1) / 5
            newUser = [['' for _ in range(7)] for _ in range(numberOfUsers + 1)]
            for form in request.form:
                if form != 'addIndivisualUser':
                    value, index = re.findall('\d+|\D+', form)
                    index = int(index)
                    data = request.form[form]
                    if not data or data == "select college":
                        continue
                    if value == 'userId':
                        newUser[index - 1][keys['memberId']] = data
                    elif value == 'username':
                        newUser[index - 1][keys['memberName']] = data
                    elif value == 'authority':
                        newUser[index - 1][keys['authority']] = data
                    elif value == 'college':
                        newUser[index - 1][keys['collegeIndex']] = data.split()[0]
                        try:
                            newUser[index - 1][keys['collegeName']] = dao.query(Colleges).\
                                                                              filter(Colleges.collegeIndex == newUser[index - 1][keys['collegeIndex']]).\
                                                                              first().\
                                                                              collegeName
                        except:
                            error = 'Wrong college index has inserted'
                            return render_template('/server_add_user.html', 
                                                   error = error,  
                                                   SETResources = SETResources,
                                                   SessionResources = SessionResources,
                                                   allColleges = allColleges,
                                                   allDepartments = allDepartments,
                                                   authorities = authorities,
                                                   newUsers = newUsers)               
                    elif value == 'department':
                        newUser[index - 1][keys['departmentIndex']] = data.split()[0]
                        try:
                            newUser[index - 1][keys['departmentName']] = dao.query(Departments).\
                                                        filter(Departments.departmentIndex == newUser[index - 1][keys['departmentIndex']]).\
                                                        first().\
                                                        departmentName
                        except:
                            error = 'Wrong department index has inserted'
                            return render_template('/server_add_user.html', 
                                                   error = error,  
                                                   SETResources = SETResources,
                                                   SessionResources = SessionResources,
                                                   allColleges = allColleges,
                                                   allDepartments = allDepartments,
                                                   authorities = authorities,
                                                   newUsers = newUsers)
                        
            for index in range(numberOfUsers+1):
                valid = True
                # check for empty row
                for col in range(7):
                    if newUser[index][col] == "":
                        valid = False
                        break
                if valid:
                    newUsers.append(newUser[index])
                    
        elif 'addUserGroup' in request.form:
            files = request.files.getlist('files')
            if list(files)[0].filename:
                # read each file
                for fileData in files:
                    # read each line    
                    for userData in fileData:
                        # slice and make information from 'key=value'
                        userInformation = userData.replace(' ', '').replace('\n', '').replace('\xef\xbb\xbf', '').split(',')
                        # userId, userName, authority, collegeIndex, collegeName, departmentIndex, departmentName
                        newUser = [''] * 7
                        
                        for eachData in userInformation:
                            if '=' in eachData:
                                # all authority is user in adding user from text file
                                newUser[keys['authority']] = 'User'
                                key = eachData.split('=')[0]
                                value = eachData.split('=')[1]
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
                                        error = 'Wrong college index has inserted'
                                        return render_template('/server_add_user.html', 
                                                               error = error,  
                                                               SETResources = SETResources,
                                                               SessionResources = SessionResources,
                                                               allColleges = allColleges,
                                                               allDepartments = allDepartments,
                                                               authorities = authorities,
                                                               newUsers = newUsers)
                                        
                                elif key == 'department':
                                    newUser[keys['departmentIndex']] = value
                                    try:
                                        newUser[keys['departmentName']] = dao.query(Departments).\
                                                         filter(Departments.departmentIndex == value).\
                                                         first().\
                                                         departmentName
                                                         
                                    except:
                                        error = 'Wrong department index has inserted'
                                        return render_template('/server_add_user.html', 
                                                               error = error,  
                                                               SETResources = SETResources,
                                                               SessionResources = SessionResources,
                                                               allColleges = allColleges,
                                                               allDepartments = allDepartments,
                                                               authorities = authorities,
                                                               newUsers = newUsers)
                                        
                                else:
                                    error = 'Try again after check the manual'
                                    return render_template('/server_add_user.html', 
                                                           error = error,  
                                                           SETResources = SETResources,
                                                           SessionResources = SessionResources,
                                                           allColleges = allColleges,
                                                           allDepartments = allDepartments,
                                                           authorities = authorities,
                                                           newUsers = newUsers)
                                    
                            else:
                                error = 'Try again after check the manual'
                                return render_template('/server_add_user.html', 
                                                       error = error,  
                                                       SETResources = SETResources,
                                                       SessionResources = SessionResources,
                                                       allColleges = allColleges,
                                                       allDepartments = allDepartments,
                                                       authorities = authorities,
                                                       newUsers = newUsers)
                        
                        for user in newUsers:
                            if user[keys['memberId']] == newUser[keys['memberId']] and\
                               user[keys['collegeIndex']] == newUser[keys['collegeIndex']] and\
                               user[keys['departmentIndex']] == newUser[keys['departmentIndex']]:
                                error = 'There is a duplicated user id. Check the file and added user list'
                                return render_template('/server_add_user.html', 
                                                       error = error,  
                                                       SETResources = SETResources,
                                                       SessionResources = SessionResources,
                                                       allColleges = allColleges,
                                                       allDepartments = allDepartments,
                                                       authorities = authorities,
                                                       newUsers = newUsers)
                                
                        newUsers.append(newUser)
                        
        elif 'addUser' in request.form:
            for newUser in newUsers:
                try:
                    if newUser[keys['authority']] == 'Course Admin':
                        newUser[keys['authority']] = SETResources().const.COURSE_ADMINISTRATOR
                    elif newUser[keys['authority']] == 'User':
                        newUser[keys['authority']] = SETResources().const.USER
                    else: # wrong access
                        error = 'Wrong access'
                        return render_template('/server_add_user.html', 
                                               error = error,  
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               allColleges = allColleges,
                                               allDepartments = allDepartments,
                                               authorities = authorities,
                                               newUsers = newUsers)

                    freshman = Members(memberId = newUser[keys['memberId']], 
                                       password = newUser[keys['memberId']], 
                                       memberName = newUser[keys['memberName']], 
                                       authority = newUser[keys['authority']],
                                       signedInDate = datetime.now())
                    dao.add(freshman)
                    dao.commit()
                except:
                    dao.rollback()
                
                try:
                    departmentInformation = DepartmentsDetailsOfMembers(memberId = newUser[keys['memberId']], 
                                                                        collegeIndex = newUser[keys['collegeIndex']], 
                                                                        departmentIndex = newUser[keys['departmentIndex']])
                    dao.add(departmentInformation)
                    dao.commit()
                except:
                    dao.rollback()
                    
                    
            newUsers = [] # initialize add user list
            if error:
                return redirect(url_for('.server_add_user'))
            
            return redirect(url_for('.server_manage_user'))
            
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
    
    return render_template('/server_add_user.html', 
                           error = error,  
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           allColleges = allColleges,
                           allDepartments = allDepartments,
                           authorities = authorities,
                           newUsers = newUsers)

@GradeServer.route('/master/manage_service')
@check_invalid_access
@login_required
def server_manage_service():        
    error = None
    return render_template('/server_manage_service.html',
                           error = error,
                           SETResources = SETResources,
                           SessionResources = SessionResources)