#-*- coding: utf-8 -*-

import os
import sys
import shutil
import glob
import re

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, \
send_file, make_response, current_app, session, flash
from werkzeug import secure_filename
from datetime import datetime

from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils.loginRequired import login_required
from GradeServer.controller.problem import *
from GradeServer.model.members import Members
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.problems import Problems
from GradeServer.model.submittedFiles import SubmittedFiles
from GradeServer.model.submissions import Submissions
from GradeServer.model.languages import Languages
from GradeServer.model.languagesOfCourses import LanguagesOfCourses
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.registeredProblems import RegisteredProblems
from GradeServer.GradeServer_config import GradeServerConfig
from GradeServer.utils.utilMessages import unknown_error
from sqlalchemy import and_, func
from GradeServer.celeryServer import Grade

# Initialize the Flask application
ALLOWED_EXTENSIONS = set(['py', 'java', 'class', 'c', 'cpp', 'h'])
errorMessages = ["DB 에러입니다.",  "서버 오류입니다. 다시 제출해 주세요.",  "파일 저장 오류"]
folderPath = [GradeServerConfig.UPLOAD_FOLDER, GradeServerConfig.CURRENT_FOLDER]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@GradeServer.route('/problem_<courseId>_<problemId>', methods = ['POST'])
@login_required
def upload(courseId, problemId):
    memberId = session['memberId']
    fileIndex = 1
    try:
        courseName = dao.query(RegisteredCourses.courseName).\
                         filter(RegisteredCourses.courseId == courseId).\
                         first().\
                         courseName
    except Exception as e:
        return unknown_error(errorMessages[0])
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
    except Exception as e:
        return unknown_error(errorMessages[0])
    
    tempPath = '%s/%s/%s_%s/%s_%s' %(folderPath[0], memberId, courseId, courseName, problemId, problemName)
    filePath = '%s/%s_%s/%s_%s/%s' %(folderPath[1], courseId, courseName, problemId, problemName, memberId)
    nonSpaceTempPath = tempPath.replace(' ', '')
    nonSpaceFilePath = filePath.replace(' ', '')

    upload_files = request.files.getlist('file[]')
    sumOfSubmittedFileSize = 0
    usedLanguage = 0
    usedLanguageVersion = 0

    if not os.path.exists(nonSpaceFilePath):
        os.makedirs(nonSpaceFilePath)
    if not os.path.exists(nonSpaceTempPath):
        os.makedirs(nonSpaceTempPath)
    else:
        for filename in glob.glob(os.path.join(nonSpaceTempPath, '*.*')):
            os.remove(filename)
    try:
        dao.query(SubmittedFiles).\
            filter(and_(SubmittedFiles.memberId == memberId,
                        SubmittedFiles.problemId == problemId,
                        SubmittedFiles.courseId == courseId)).\
            delete()
        dao.commit()
    except Exception as e:
        return unknown_error(errorMessages[0])
    
    usedLanguageName = request.form['usedLanguageName']

    try:
        for file in upload_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                try:
                    file.save(os.path.join(nonSpaceTempPath, filename))
                except:
                    return unknown_error(errorMessages[2])
                fileSize = os.stat(os.path.join(nonSpaceTempPath, filename)).st_size
                    
                try:
                    usedLanguage = dao.query(Languages.languageIndex).\
                                       filter(Languages.languageName == usedLanguageName).\
                                       first().\
                                       languageIndex
                except Exception as e:
                    return unknown_error(errorMessages[0])
                                                        
                try:
                    submittedFiles = SubmittedFiles(memberId = memberId,
                                                    problemId = problemId,
                                                    courseId = courseId,
                                                    fileIndex = fileIndex,
                                                    fileName = filename,
                                                    filePath = nonSpaceFilePath,
                                                    fileSize = fileSize)                
                    dao.add(submittedFiles)
                    dao.commit()
                except Exception as e:
                    dao.rollback()
                    return unknown_error(errorMessages[0])            
                fileIndex += 1
                sumOfSubmittedFileSize += fileSize
    except:
        for filename in glob.glob(os.path.join(nonSpaceTempPath, '*.*')):
            os.remove(filename)
        if len(glob.glob(os.path.join(nonSpaceFilePath, '*.*'))) > 0:
            for filename in glob.glob(os.path.join(nonSpaceFilePath, '*.*')):
                shutil.copy(filename, nonSpaceTempPath)
        return unknown_error(errorMessages[1])
         
    insert_to_db(courseId, memberId, problemId, nonSpaceFilePath, nonSpaceTempPath, usedLanguage, sumOfSubmittedFileSize, problemName, usedLanguageName)
               
    return courseId
        
@GradeServer.route('/problem_<courseId>_page<pageNum>_<problemId>', methods = ['POST'])
@login_required
def code(courseId, pageNum, problemId):
    memberId = session['memberId']
    fileIndex = 1
    usedLanguage = 0
    usedLanguageVersion = 0
    try:
        courseName = dao.query(RegisteredCourses.courseName).\
                         filter(RegisteredCourses.courseId == courseId).\
                         first().\
                         courseName
    except Exception as e:
        return unknown_error(errorMessages[0])
    
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
    except Exception as e:
        return unknown_error(errorMessages[0])
    
    tempPath = '%s/%s/%s_%s/%s_%s' %(folderPath[0], memberId, courseId, courseName, problemId, problemName)
    filePath = '%s/%s_%s/%s_%s/%s' %(folderPath[1], courseId, courseName, problemId, problemName, memberId)
    nonSpaceTempPath = tempPath.replace(' ', '')
    nonSpaceFilePath = filePath.replace(' ', '')
    if not os.path.exists(nonSpaceFilePath):
        os.makedirs(nonSpaceFilePath)
    if not os.path.exists(nonSpaceTempPath):
        os.makedirs(nonSpaceTempPath)
    else:
        for filename in glob.glob(os.path.join(nonSpaceTempPath, '*.*')):
            os.remove(filename)
    try:
        dao.query(SubmittedFiles).\
            filter(and_(SubmittedFiles.memberId == memberId,
                        SubmittedFiles.problemId == problemId,
                        SubmittedFiles.courseId == courseId)).\
            delete()
        dao.commit()
    except Exception as e:
        dao.rollback()
        return unknown_error(errorMessages[0])
        
    tests = request.form['copycode']
    unicode(tests)
    tests = tests.replace('\r\n', '\n')
    usedLanguageName = request.form['language']
    
    if usedLanguageName == 'C':
        filename = 'test.c'
    
    elif usedLanguageName == 'C++':
        filename = 'test.cpp'
    
    elif usedLanguageName == 'JAVA':
        className = re.search(r'public\s+class\s+(\w+)', tests)
        try:
            filename = '%s.java' %(className.group(1))
        except:
            filename = 'missClassName.java'
        
    elif usedLanguageName == 'PYTHON':
        filename = 'test.py'
        
    try:
        fout = open(os.path.join(nonSpaceTempPath, filename), 'w')
        fout.write(tests)
        fout.close()
    except:
        return unknown_error(errorMessages[2])
    try:
        usedLanguage = dao.query(Languages.languageIndex).\
                           filter(Languages.languageName == usedLanguageName).\
                           first().\
                           languageIndex
    except Exception as e:
        return unknown_error(errorMessages[0])
    
    sumOfSubmittedFileSize = os.stat(os.path.join(nonSpaceTempPath, filename)).st_size
    
    try:
        submittedFiles = SubmittedFiles(memberId = memberId,
                                        problemId = problemId,
                                        courseId = courseId,
                                        fileIndex = fileIndex,
                                        fileName = filename,
                                        filePath = nonSpaceFilePath,
                                        fileSize = sumOfSubmittedFileSize)                
        dao.add(submittedFiles)
        dao.commit()
    except Exception as e:
        dao.rollback()
        return unknown_error(errorMessages[0]) 
    
    insert_to_db(courseId, memberId, problemId, nonSpaceFilePath, nonSpaceTempPath, usedLanguage, sumOfSubmittedFileSize, problemName, usedLanguageName)
    
    return redirect(url_for('.problemList',
                            courseId = courseId,
                            pageNum = pageNum))
    
def insert_to_db(courseId, memberId, problemId, nonSpaceFilePath, nonSpaceTempPath, usedLanguage, sumOfSubmittedFileSize, problemName, usedLanguageName):
    for filename in glob.glob(os.path.join(nonSpaceFilePath, '*.*')):
        os.remove(filename)
            
    for filename in glob.glob(os.path.join(nonSpaceTempPath, '*.*')):
        shutil.copy(os.path.join(nonSpaceTempPath, filename), nonSpaceFilePath)
        
    try:
        usedLanguageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        return unknown_error(errorMessages[0])

    try:
        subCount = dao.query(func.max(Submissions.submissionCount).label ('submissionCount')).\
                       filter(Submissions.memberId == memberId,
                              Submissions.courseId == courseId,
                              Submissions.problemId == problemId).\
                       first()
        subCountNum = subCount.submissionCount + 1
    except:
        subCountNum = 1

    try:
        solCount = dao.query(Submissions.solutionCheckCount).\
                       filter(Submissions.memberId == memberId,
                              Submissions.courseId == courseId,
                              Submissions.problemId == problemId,
                              Submissions.submissionCount == subCount.submissionCount).\
                       first()
        solCountNum = solCount.solutionCheckCount
    except:
        solCountNum = 0
    
    try:
        submissions = Submissions(memberId = memberId,
                                  problemId = problemId,
                                  courseId = courseId,
                                  submissionCount = subCountNum,
                                  solutionCheckCount = solCountNum,
                                  status = 'Judging',
                                  codeSubmissionDate = datetime.now(),
                                  sumOfSubmittedFileSize = sumOfSubmittedFileSize,
                                  usedLanguage = usedLanguage,
                                  usedLanguageVersion = usedLanguageVersion)
        dao.add(submissions)
        dao.commit()
    except Exception as e:
        dao.rollback()
        return unknown_error(errorMessages[0])
            
    flash('submission success!')
    
    try:
        problemsParam = dao.query(Problems.problemPath,
                                  Problems.limitedTime,
                                  Problems.limitedMemory,
                                  Problems.solutionCheckType).\
                                  filter(Problems.problemId == problemId).\
                                  first()
                                      
        problemPath = problemsParam[0]
        limitedTime = problemsParam[1]
        limitedMemory = problemsParam[2]
        solutionCheckType = problemsParam[3]
        problemCasesPath = '%s/%s_%s_%s' %(problemPath, problemId, problemName, solutionCheckType)
    except Exception as e:
        return unknown_error(errorMessages[0])
    try:
        departmentIndex = dao.query(DepartmentsDetailsOfMembers.departmentIndex).\
                              filter(DepartmentsDetailsOfMembers.memberId == memberId).\
                              first().\
                              departmentIndex
    except Exception as e:
        return unknown_error(errorMessages[0])
    try:
        isAllInputCaseInOneFile = dao.query(RegisteredProblems.isAllInputCaseInOneFile).\
                                      filter(RegisteredProblems.problemId == problemId,
                                             RegisteredProblems.courseId == courseId).\
                                      first().\
                                      isAllInputCaseInOneFile
    except Exception as e:
        return unknown_error(errorMessages[0])
    
    caseCount = len(glob.glob(os.path.join(problemCasesPath, '*.*')))/2
    
    if caseCount > 1:
        if isAllInputCaseInOneFile == 'MultipleFiles':
            caseCount -= 1
        else:
            caseCount = 1
            
    Grade.delay(str(nonSpaceFilePath),
                str(problemPath),
                str(memberId),
                str(problemId),
                str(solutionCheckType),
                caseCount,
                limitedTime,
                limitedMemory,
                str(usedLanguageName),
                str(usedLanguageVersion),
                str(courseId),
                subCountNum)
