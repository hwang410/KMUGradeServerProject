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
from GradeServer.GradeServer_config import GradeServerConfig
from sqlalchemy import and_, func
from celeryServer_existingcontainer import Grade

# Initialize the Flask application
ALLOWED_EXTENSIONS = set(['py', 'java', 'class', 'c', 'cpp', 'h', 'jar'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@GradeServer.route('/problem/<courseId>/<problemId>/upload', methods = ['POST'])
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
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e
    
    tempPath = '/mnt/shared/Temp/%s/%s_%s/%s_%s' %(memberId, courseId, courseName, problemId, problemName)
    filePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s/%s' %(courseId, courseName, problemId, problemName, memberId)
    
    upload_files = request.files.getlist('file[]')
    filenames = []
    sumOfSubmittedFileSize = 0
    usedLanguage = 1
    usedLanguageVersion = 0
    
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)
    
    try:
        dao.query(SubmittedFiles).\
            filter(and_(SubmittedFiles.memberId == memberId,
                        SubmittedFiles.problemId == problemId,
                        SubmittedFiles.courseId == courseId)).\
            delete()
        dao.commit()
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e 
    
    try:
        for file in upload_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(tempPath, filename))
                fileSize = os.stat(tempPath + '/' + filename).st_size
                filenames.append(filename)
                shutil.copy(os.path.join(tempPath, filename), filePath )
                
                if filename.rsplit('.', 1)[1] == 'c':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'C').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        dao.rollback()
                        print 'DB error : ' + str(e)
                        raise e 
                elif filename.rsplit('.', 1)[1] == 'cpp':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'C++').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        dao.rollback()
                    print 'DB error : ' + str(e)
                    raise e                                                                    
                elif filename.rsplit('.', 1)[1] == 'java':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'JAVA').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        dao.rollback()
                        print 'DB error : ' + str(e)
                        raise e
                elif filename.rsplit('.', 1)[1] == 'py':
                    try:
                        usedLanguage = dao.query(Languages.languageIndex).\
                                           filter(Languages.languageName == 'PYTHON').\
                                           first().\
                                           languageIndex
                    except Exception as e:
                        dao.rollback()
                        print 'DB error : ' + str(e)
                        raise e
                                                                     
                              
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
                    print 'DB error : ' + str(e)
                    raise e            
                fileIndex += 1
                sumOfSubmittedFileSize += fileSize
    except:
        for filename in glob.glob(os.path.join(tempPath, '*.*')):
            os.remove(filename)
        for filename in glob.glob(os.path.join(filePath, '*.*')):
            shutil.copy(filename, tempPath)
        
    try:
        usedLanguageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e

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
                                  codeSubmissionDate = datetime.now(),
                                  sumOfSubmittedFileSize = sumOfSubmittedFileSize,
                                  usedLanguage = usedLanguage,
                                  usedLanguageVersion = usedLanguageVersion)
        dao.add(submissions)
        dao.commit()
    except Exception as e:
        print 'DB error : ' + str(e)
        raise e
          
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
    except Exception as e:
        print 'DB error : ' + str(e)
        raise e
    try:
        departmentIndex = dao.query(DepartmentsDetailsOfMembers.departmentIndex).\
                              filter(DepartmentsDetailsOfMembers.memberId == memberId).\
                              first().\
                              departmentIndex
    except Exception as e:
        print 'DB error : ' + str(e)
        raise e
    
    caseCount = len(glob.glob(problemsParam[0]))/2
    
    if caseCount > 1:
        if departmentIndex == 1:
           caseCount -= 1
        else:
            caseCount = 1
            
    """Grade.delay(filePath,
           problemPath,
           memberId,
           problemId,
           solutionCheckType,
           caseCount,
           limitedTime,
           limitedMemory,
           usedLanguage,
           usedLanguageVersion,
           courseId,
           subCount)"""
           
    return courseId
        
@GradeServer.route('/problem/<courseId>/<problemId>/codesubmission', methods = ['POST'])
@login_required
def code(courseId, problemId):
    
    memberId = session['memberId']
    fileIndex = 1
    usedLanguage = 1
    usedLanguageVersion = 0
    try:
        courseName = dao.query(RegisteredCourses.courseName).\
                         filter(RegisteredCourses.courseId == courseId).\
                         first().\
                         courseName
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e
    filePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s/%s' %(courseId, courseName, problemId, problemName, memberId)
    
    try:
        dao.query(SubmittedFiles).\
            filter(and_(SubmittedFiles.memberId == memberId,
                        SubmittedFiles.problemId == problemId,
                        SubmittedFiles.courseId == courseId)).\
            delete()
        dao.commit()
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e 
    
    tests = request.form['copycode']
    unicode(tests)
    tests = tests.replace('\r\n', '\n')

    num = request.form['language']

    if num == '1':
        filename = 'test.c'
        fout = open(filePath + '/' + filename, 'w')
        fout.write(tests)
        fout.close()
        try:
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'C').\
                               first().\
                               languageIndex
        except Exception as e:
            dao.rollback()
            print 'DB error : ' + str(e)
            raise e 
    
    elif num == '2':
        filename = 'test.cpp'
        fout = open(filePath + '/' + filename, 'w')
        fout.write(tests)
        fout.close()
        try:
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'C++').\
                               first().\
                               languageIndex
        except Exception as e:
            dao.rollback()
            print 'DB error : ' + str(e)
            raise e 
    
    elif num == '3':
        filename = 'test.java'
        fout = open(filePath + '/' + filename, 'w')
        fout.write(tests)
        fout.close()
        try:
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'JAVA').\
                               first().\
                               languageIndex
        except Exception as e:
            dao.rollback()
            print 'DB error : ' + str(e)
            raise e 
        
    elif num == '4':
        filename = 'test.py'
        fout = open(filePath + '/' + filename, 'w')
        fout.write(tests)
        fout.close()
        try:
            usedLanguage = dao.query(Languages.languageIndex).\
                               filter(Languages.languageName == 'PYTHON').\
                               first().\
                               languageIndex
        except Exception as e:
            dao.rollback()
            print 'DB error : ' + str(e)
            raise e 
        
    fileSize = os.stat(filePath + '/' + filename).st_size
    
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
        print 'DB error : ' + str(e)
        raise e
    
    try:
        usedLanguageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise e   
    
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
        solCount = dao.query(func.max(Submissions.solutionCheckCount).label('solutionCheckCount')).\
                       filter(Submissions.memberId == memberId,
                                    Submissions.courseId == courseId,
                                    Submissions.problemId == problemId).\
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
                                  codeSubmissionDate = datetime.now(),
                                  sumOfSubmittedFileSize = fileSize,
                                  usedLanguage = usedLanguage,
                                  usedLanguageVersion = usedLanguageVersion)
        dao.add(submissions)
        dao.commit()
    except Exception as e:
        print 'DB error : ' + str(e)
        raise e
    
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
    except Exception as e:
        print 'DB error : ' + str(e)
        raise e
    try:
        departmentIndex = dao.query(DepartmentsDetailsOfMembers.departmentIndex).\
                              filter(DepartmentsDetailsOfMembers.memberId == memberId).\
                              first().\
                              departmentIndex
    except Exception as e:
        print 'DB error : ' + str(e)
        raise e
    
    caseCount = len(glob.glob(problemsParam[0]))/2
    
    if caseCount > 1:
        if departmentIndex == 1:
           caseCount -= 1
        else:
            caseCount = 1
            
    """Grade.delay(filePath,
           problemPath,
           memberId,
           problemId,
           solutionCheckType,
           caseCount,
           limitedTime,
           limitedMemory,
           usedLanguage,
           usedLanguageVersion,
           courseId,
           subCount)"""
    
    flash('submission success!')
    return redirect(url_for('.problemList',
                            courseId = courseId))