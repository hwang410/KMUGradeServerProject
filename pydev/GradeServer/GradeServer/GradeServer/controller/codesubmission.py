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
#from GradeServer.controller.problem import *
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
from sqlalchemy import and_, func, select
from GradeServer.celeryServer import Grade
from os.path import exists

# Initialize the Flask application
errorMessages = ["DB 에러입니다.",  "서버 오류입니다. 다시 제출해 주세요.",  "파일 저장 오류"]
PATH = GradeServerConfig.CURRENT_FOLDER

class MakePath:
    def __init__(self, path, memberId, courseId, courseName, problemId, problemName, submissionCount):
        self.path = path
        self.memberId = memberId
        self.courseId = courseId
        self.courseName = courseName
        self.problemId = problemId
        self.problemName = problemName
        self.submissionCount = '%s_%s' %('sub', str(submissionCount))
    def make_current_path(self):
        result = '%s/%s_%s/%s_%s/%s/%s' %(self.path, self.courseId, self.courseName, self.problemId, self.problemName, self.memberId, self.submissionCount)
        return result.replace(' ', '')

class InsertToSubmittedFiles:
    def __init__(self, memberId, courseId, problemId, fileIndex, fileName, filePath, fileSize):
        self.memberId = memberId
        self.courseId = courseId
        self.problemId = problemId
        self.fileIndex = fileIndex
        self.fileName = fileName
        self.filePath = filePath
        self.fileSize = fileSize
        
def course_name(courseId):
    try:
        courseName = dao.query(RegisteredCourses.courseName).\
                         filter(RegisteredCourses.courseId == courseId).\
                         first().\
                         courseName
        return courseName
    except Exception as e:
        return unknown_error(errorMessages[0])
    
def problem_name(problemId):
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
        return problemName
    except Exception as e:
        return unknown_error(errorMessages[0])

def get_submission_count(memberId, courseId, problemId):
    try:
        subCount = dao.query(func.max(Submissions.submissionCount).label ('submissionCount')).\
                       filter(Submissions.memberId == memberId,
                              Submissions.courseId == courseId,
                              Submissions.problemId == problemId).\
                       first()
        subCountNum = subCount.submissionCount + 1
    except:
        subCountNum = 1
    return subCountNum

def get_solution_check_count(memberId, courseId, problemId, subCountNum):
    try:
        solCount = dao.query(Submissions.solutionCheckCount).\
                       filter(Submissions.memberId == memberId,
                              Submissions.courseId == courseId,
                              Submissions.problemId == problemId,
                              Submissions.submissionCount == subCountNum).\
                       first()
        solCountNum = solCount.solutionCheckCount
    except:
        solCountNum = 0
    return solCountNum

def insert_submitted_files(insertSubmittedFilesObject):
    submittedFiles = SubmittedFiles(memberId = insertSubmittedFilesObject.memberId,
                                    problemId = insertSubmittedFilesObject.problemId,
                                    courseId = insertSubmittedFilesObject.courseId,
                                    fileIndex = insertSubmittedFilesObject.fileIndex,
                                    fileName = insertSubmittedFilesObject.fileName,
                                    filePath = insertSubmittedFilesObject.filePath,
                                    fileSize = insertSubmittedFilesObject.fileSize)                
    dao.add(submittedFiles)
    
def get_used_language(usedLanguageName):
    try:
        usedLanguage = dao.query(Languages.languageIndex).\
                           filter(Languages.languageName == usedLanguageName).\
                           first().\
                           languageIndex
    except Exception as e:
        return unknown_error(errorMessages[0])
    return usedLanguage

def get_problem_info(problemId, problemName):
    try:
        problemPath, limitedTime, limitedMemory, solutionCheckType = dao.query(Problems.problemPath,
                                                                               Problems.limitedTime,
                                                                               Problems.limitedMemory,
                                                                               Problems.solutionCheckType).\
                                                                         filter(Problems.problemId == problemId).\
                                                                         first()
        problemCasesPath = '%s/%s_%s_%s' %(problemPath, problemId, problemName, solutionCheckType)
    except Exception as e:
        return unknown_error(errorMessages[0])
    return problemPath, limitedTime, limitedMemory, solutionCheckType, problemCasesPath

def is_support_multiple_case(problemId, courseId):
    try:
        isAllInputCaseInOneFile = dao.query(RegisteredProblems.isAllInputCaseInOneFile).\
                                      filter(RegisteredProblems.problemId == problemId,
                                             RegisteredProblems.courseId == courseId).\
                                      first().\
                                      isAllInputCaseInOneFile
    except Exception as e:
        return unknown_error(errorMessages[0])
    return isAllInputCaseInOneFile

def used_language_version(courseId, usedLanguage):
    try:
        usedLanguageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        return unknown_error(errorMessages[0])
    return usedLanguageVersion
@GradeServer.route('/problem_<courseId>_<problemId>', methods = ['POST'])
@login_required
def upload(courseId, problemId):
    memberId = session['memberId']
    fileIndex = 1
    
    courseName = course_name(courseId)
    problemName = problem_name(problemId)
    subCountNum = get_submission_count(memberId, courseId, problemId)
    
    makePath = MakePath(PATH, memberId, courseId, courseName, problemId, problemName, subCountNum)
    filePath = makePath.make_current_path()
    makePath = MakePath(PATH, memberId, courseId, courseName, problemId, problemName, subCountNum-1)
    deletePath = makePath.make_current_path()
    sumOfSubmittedFileSize = 0
    usedLanguage = 0
    usedLanguageVersion = 0

    os.makedirs(filePath)
    
    try:
        dao.query(SubmittedFiles).\
            filter(and_(SubmittedFiles.memberId == memberId,
                        SubmittedFiles.problemId == problemId,
                        SubmittedFiles.courseId == courseId)).\
            delete()
        dao.commit()
    except Exception as e:
        return unknown_error(errorMessages[0])

    try:
        upload_files = request.files.getlist('file[]')
        for file in upload_files:
            fileName = secure_filename(file.filename)
            
            try:
                file.save(os.path.join(filePath, fileName))
            except:
                return unknown_error(errorMessages[2])
            
            fileSize = os.stat(os.path.join(filePath, fileName)).st_size                                          
            insertSubmittedFilesObject = InsertToSubmittedFiles(memberId, courseId, problemId, fileIndex, fileName, filePath, fileSize)
            insert_submitted_files(insertSubmittedFilesObject)
           
            fileIndex += 1
            sumOfSubmittedFileSize += fileSize
        dao.commit()
    except:
        dao.rollback()
        os.system("rm -rf %s" % filePath)
        return unknown_error(errorMessages[1])

    os.system("rm -rf %s" % deletePath)
    usedLanguageName = request.form['usedLanguageName']
    usedLanguage = get_used_language(usedLanguageName)
    usedLanguageVersion = used_language_version(courseId, usedLanguage)
    solCountNum = get_solution_check_count(memberId, courseId, problemId, subCountNum)
    insert_to_sumbissions(courseId, memberId, problemId, filePath, subCountNum, solCountNum, usedLanguage, usedLanguageVersion, sumOfSubmittedFileSize, problemName, usedLanguageName)
    problemPath, limitedTime, limitedMemory, solutionCheckType, problemCasesPath = get_problem_info(problemId, problemName)

    isAllInputCaseInOneFile = is_support_multiple_case(problemId, courseId)
    
    caseCount = len(glob.glob(os.path.join(problemCasesPath, '*.*')))/2
    
    if caseCount > 1:
        if isAllInputCaseInOneFile == 'MultipleFiles':
            caseCount -= 1
        else:
            caseCount = 1
    send_to_celery(filePath,
                   problemPath,
                   memberId,
                   problemId,
                   solutionCheckType,
                   caseCount,
                   limitedTime,
                   limitedMemory,
                   usedLanguageName,
                   usedLanguageVersion,
                   courseId,
                   subCountNum)
    flash('submission success!')
    return "0"

@GradeServer.route('/problem_<courseId>_page<pageNum>_<problemId>', methods = ['POST'])
@login_required
def code(courseId, pageNum, problemId):
    memberId = session['memberId']
    fileIndex = 1
    usedLanguage = 0
    usedLanguageVersion = 0
    
    courseName = course_name(courseId)
    problemName = problem_name(problemId)
    subCountNum = get_submission_count(memberId, courseId, problemId)
    
    makePath = MakePath(PATH, memberId, courseId, courseName, problemId, problemName, subCountNum)
    filePath = makePath.make_current_path()
    makePath = MakePath(PATH, memberId, courseId, courseName, problemId, problemName, subCountNum-1)
    deletePath = makePath.make_current_path()
    
    os.makedirs(filePath)
    
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
        fileName = 'test.c'
    
    elif usedLanguageName == 'C++':
        fileName = 'test.cpp'
    
    elif usedLanguageName == 'JAVA':
        className = re.search(r'public\s+class\s+(\w+)', tests)
        try:
            fileName = '%s.java' %(className.group(1))
        except:
            fileName = 'missClassName.java'
        
    elif usedLanguageName == 'PYTHON':
        fileName = 'test.py'
        
    try:
        fout = open(os.path.join(filePath, fileName), 'w')
        fout.write(tests)
        fout.close()
    except:
        os.system("rm -rf %s" % filePath)
        return unknown_error(errorMessages[2])

    os.system("rm -rf %s" % deletePath)    
    fileSize = os.stat(os.path.join(filePath, fileName)).st_size
    
    insertSubmittedFilesObject = InsertToSubmittedFiles(memberId, courseId, problemId, fileIndex, fileName, filePath, fileSize)
    try:
        insert_submitted_files(insertSubmittedFilesObject)
    except Exception as e:
        dao.rollback()
        return unknown_error(errorMessages[0]) 
    dao.commit()
    
    usedLanguage = get_used_language(usedLanguageName)
    usedLanguageVersion = used_language_version(courseId, usedLanguage)
    solCountNum = get_solution_check_count(memberId, courseId, problemId, subCountNum)
    insert_to_sumbissions(courseId, memberId, problemId, filePath, subCountNum, solCountNum, usedLanguage, usedLanguageVersion, fileSize, problemName, usedLanguageName)
    
    problemPath, limitedTime, limitedMemory, solutionCheckType, problemCasesPath = get_problem_info(problemId, problemName)

    isAllInputCaseInOneFile = is_support_multiple_case(problemId, courseId)
    
    caseCount = len(glob.glob(os.path.join(problemCasesPath, '*.*')))/2
    
    if caseCount > 1:
        if isAllInputCaseInOneFile == 'MultipleFiles':
            caseCount -= 1
        else:
            caseCount = 1
            
    send_to_celery(filePath,
                   problemPath,
                   memberId,
                   problemId,
                   solutionCheckType,
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
    
def insert_to_sumbissions(courseId, memberId, problemId, filePath, subCountNum, solCountNum, usedLanguage, usedLanguageVersion, sumOfSubmittedFileSize, problemName, usedLanguageName):
        
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
        
    except Exception as e:
        dao.rollback()
        return unknown_error(errorMessages[0])
    dao.commit()
    """try:
        departmentIndex = dao.query(DepartmentsDetailsOfMembers.departmentIndex).\
                              filter(DepartmentsDetailsOfMembers.memberId == memberId).\
                              first().\
                              departmentIndex
    except Exception as e:
        return unknown_error(errorMessages[0])"""
        
def send_to_celery(filePath,
                   problemPath,
                   memberId,
                   problemId,
                   solutionCheckType,
                   caseCount,
                   limitedTime,
                   limitedMemory,
                   usedLanguageName,
                   usedLanguageVersion,
                   courseId,
                   subCountNum): 
    Grade.delay(str(filePath),
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
