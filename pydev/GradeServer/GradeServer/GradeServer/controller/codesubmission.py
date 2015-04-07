#-*- coding: utf-8 -*-

import os
import sys
import shutil
import glob

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, \
send_file, make_response, current_app, session, flash
from werkzeug import secure_filename
from datetime import datetime
#from wtforms import Form, FileField, TextField, TextAreaField, HiddenField, validators

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
        unknown_error("DB 에러입니다")
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
    except Exception as e:
        unknown_error("DB 에러입니다")
    
    tempPath = '/mnt/shared/Temp/%s/%s_%s/%s_%s' %(memberId, courseId, courseName, problemId, problemName)
    filePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s/%s' %(courseId, courseName, problemId, problemName, memberId)
    nonSpaceTempPath = tempPath.replace(' ', '')
    nonSpaceFilePath = filePath.replace(' ', '')

    upload_files = request.files.getlist('file[]')
    filenames = []
    sumOfSubmittedFileSize = 0
    usedLanguage = 0
    usedLanguageVersion = 0
    
    if not os.path.exists(nonSpaceTempPath):
        os.makedirs(nonSpaceTempPath)
    
    try:
        dao.query(SubmittedFiles).\
            filter(and_(SubmittedFiles.memberId == memberId,
                        SubmittedFiles.problemId == problemId,
                        SubmittedFiles.courseId == courseId)).\
            delete()
        dao.commit()
    except Exception as e:
        unknown_error("DB 에러입니다")
    
    usedLanguageName = request.form['usedLanguageName']

    try:
        for file in upload_files:
            print file
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(nonSpaceTempPath, filename))
                fileSize = os.stat(os.path.join(nonSpaceTempPath, filename)).st_size
                filenames.append(filename)
                shutil.copy(os.path.join(nonSpaceTempPath, filename), nonSpaceFilePath)
                
                if usedLanguageName == 'C':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'C').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        unknown_error("DB 에러입니다")
                elif usedLanguageName == 'C++':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'C++').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        unknown_error("DB 에러입니다")                                                                  
                elif usedLanguageName == 'JAVA':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'JAVA').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        unknown_error("DB 에러입니다")
                elif usedLanguageName == 'PYTHON':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'PYTHON').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        unknown_error("DB 에러입니다")
                                                                     
                try:
                    submittedFiles = SubmittedFiles(memberId = memberId,
                                                    problemId = problemId,
                                                    courseId = courseId,
                                                    fileIndex = fileIndex,
                                                    fileName = filename,
                                                    filePath = filePath,
                                                    fileSize = fileSize)                
                    dao.add(submittedFiles)
                    dao.commit()
                except Exception as e:
                    dao.rollback()
                    unknown_error("DB 에러입니다")            
                fileIndex += 1
                sumOfSubmittedFileSize += fileSize
    except:
        for filename in glob.glob(os.path.join(nonSpaceTempPath, '*.*')):
            os.remove(filename)
        for filename in glob.glob(os.path.join(nonSpaceFilePath, '*.*')):
            shutil.copy(filename, nonSpaceTempPath)
        
    try:
        usedLanguageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        unknown_error("DB 에러입니다")

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
        unknown_error("DB 에러입니다")
            
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
        unknown_error("DB 에러입니다")
    try:
        departmentIndex = dao.query(DepartmentsDetailsOfMembers.departmentIndex).\
                              filter(DepartmentsDetailsOfMembers.memberId == memberId).\
                              first().\
                              departmentIndex
    except Exception as e:
        unknown_error("DB 에러입니다")
    try:
        isAllInputCaseInOneFile = dao.query(RegisteredProblems.isAllInputCaseInOneFile).\
                                      filter(RegisteredProblems.problemId == problemId,
                                             RegisteredProblems.courseId == courseId).\
                                      first().\
                                      isAllInputCaseInOneFile
    except Exception as e:
        unknown_error("DB 에러입니다")
    
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
                usedLanguageName,
                usedLanguageVersion,
                courseId,
                subCountNum)
               
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
        print unknown_error("DB 에러입니다")
    
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
    except Exception as e:
        print unknown_error("DB 에러입니다")
    
    tempPath = '/mnt/shared/Temp/%s/%s_%s/%s_%s' %(memberId, courseId, courseName, problemId, problemName)
    filePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s/%s' %(courseId, courseName, problemId, problemName, memberId)
    nonSpaceTempPath = tempPath.replace(' ', '')
    nonSpaceFilePath = filePath.replace(' ', '')
    
    if not os.path.exists(nonSpaceTempPath):
        os.makedirs(nonSpaceTempPath)
        
    try:
        dao.query(SubmittedFiles).\
            filter(and_(SubmittedFiles.memberId == memberId,
                        SubmittedFiles.problemId == problemId,
                        SubmittedFiles.courseId == courseId)).\
            delete()
        dao.commit()
    except Exception as e:
        dao.rollback()
        unknown_error("DB 에러입니다")
    tests = request.form['copycode']
    unicode(tests)
    tests = tests.replace('\r\n', '\n')
    usedLanguageName = request.form['language']

    
    if usedLanguageName == 'C':
        filename = 'test.c'
        fout = open(os.path.join(nonSpaceTempPath, filename), 'w')
        fout.write(tests)
        fout.close()
        try:
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'C').\
                               first().\
                               languageIndex
        except Exception as e:
            unknown_error("DB 에러입니다")
    
    elif usedLanguageName == 'C++':
        filename = 'test.cpp'
        fout = open(os.path.join(nonSpaceTempPath, filename), 'w')
        fout.write(tests)
        fout.close()
        try:  
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'C++').\
                               first().\
                               languageIndex
        except Exception as e:
            unknown_error("DB 에러입니다")
    
    elif usedLanguageName == 'JAVA':
        filename = 'test.java'
        fout = open(os.path.join(nonSpaceTempPath, filename), 'w')
        fout.write(tests)
        fout.close()
        try:
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'JAVA').\
                               first().\
                               languageIndex
        except Exception as e:
            unknown_error("DB 에러입니다")
        
    elif usedLanguageName == 'PYTHON':
        filename = 'test.py'
        fout = open(os.path.join(nonSpaceTempPath, filename), 'w')
        fout.write(tests)
        fout.close()
        try:
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'PYTHON').\
                               first().\
                               languageIndex
        except Exception as e:
            unknown_error("DB 에러입니다")
        
    fileSize = os.stat(os.path.join(nonSpaceTempPath, filename)).st_size
    
    try:
        submittedFiles = SubmittedFiles(memberId = memberId,
                                        problemId = problemId,
                                        courseId = courseId,
                                        fileIndex = fileIndex,
                                        fileName = filename,
                                        filePath = filePath,
                                        fileSize = fileSize)                
        dao.add(submittedFiles)
        dao.commit()                
    except Exception as e:            
        dao.rollback()
        unknown_error("DB 에러입니다")
    
    try:
        usedLanguageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        unknown_error("DB 에러입니다") 
    
    try:
        subCount = dao.query(func.max(Submissions.submissionCount).label('submissionCount')).\
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
                                  sumOfSubmittedFileSize = fileSize,
                                  usedLanguage = usedLanguage,
                                  usedLanguageVersion = usedLanguageVersion)
        dao.add(submissions)
        dao.commit()
    except Exception as e:
        dao.rollback()
        unknown_error("DB 에러입니다")
    
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
        unknown_error("DB 에러입니다")
    try:
        departmentIndex = dao.query(DepartmentsDetailsOfMembers.departmentIndex).\
                              filter(DepartmentsDetailsOfMembers.memberId == memberId).\
                              first().\
                              departmentIndex
    except Exception as e:
        unknown_error("DB 에러입니다")
    
    try:
        isAllInputCaseInOneFile = dao.query(RegisteredProblems.isAllInputCaseInOneFile).\
                                      filter(RegisteredProblems.problemId == problemId,
                                             RegisteredProblems.courseId == courseId).\
                                      first().\
                                      isAllInputCaseInOneFile
    except Exception as e:
        unknown_error("DB 에러입니다")
    
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
                usedLanguageName,
                usedLanguageVersion,
                courseId,
                subCountNum)
    
    flash('submission success!')
    return redirect(url_for('.problemList',
                            courseId = courseId,
                            pageNum = pageNum))
