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
from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.routeResources import RouteResources
from sqlalchemy import and_, func, update
from GradeServer.celeryServer import Grade
from os.path import exists
from GradeServer.utils.utilMessages import get_message

# Initialize the Flask application
PATH = GradeServerConfig.CURRENT_FOLDER

class MakePath:
    def __init__(self, path, memberId, memberName, courseId, courseName, problemId, problemName):
        self.path = path
        self.memberId = memberId
        self.memberName = memberName
        self.courseId = courseId
        self.courseName = courseName
        self.problemId = problemId
        self.problemName = problemName
    def make_current_path(self):
        result = '%s/%s_%s/%s_%s/%s_%s' %(self.path, self.courseId, self.courseName, self.memberId, 
self.memberName, self.problemId, self.problemName)
        return result.replace(' ', '')
    def make_temp_path(self):
        result = '%s/%s_%s/%s_%s/%s_%s_tmp' %(self.path, self.courseId, self.courseName, self.memberId, 
self.memberName, self.problemId, self.problemName)
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
        
def get_course_name(courseId):
    try:
        courseName = dao.query(RegisteredCourses.courseName).\
                         filter(RegisteredCourses.courseId == courseId).\
                         first().\
                         courseName
        return courseName
    except Exception as e:
        return unknown_error('dbError')
    
def get_problem_name(problemId):
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
        return problemName
    except Exception as e:
        return unknown_error('dbError')

def get_member_name(memberId):
    try:
        memberName = dao.query(Members.memberName).\
                         filter(Members.memberId == memberId).\
                         first().\
                         memberName
        return memberName
    except Exception as e:
        return unknown_error('dbError')

def get_submission_count(memberId, courseId, problemId):
    try:
        subCount = dao.query(func.max(Submissions.submissionCount).\
                       label(OtherResources.const.SUBMISSION_COUNT)).\
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
        return unknown_error('dbError')
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
        return unknown_error('dbError')
    return problemPath, limitedTime, limitedMemory, solutionCheckType, problemCasesPath

def is_support_multiple_case(problemId, courseId):
    try:
        isAllInputCaseInOneFile = dao.query(RegisteredProblems.isAllInputCaseInOneFile).\
                                      filter(RegisteredProblems.problemId == problemId,
                                             RegisteredProblems.courseId == courseId).\
                                      first().\
                                      isAllInputCaseInOneFile
    except Exception as e:
        return unknown_error('dbError')
    return isAllInputCaseInOneFile

def used_language_version(courseId, usedLanguage):
    try:
        usedLanguageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        return unknown_error('dbError')
    return usedLanguageVersion

def get_case_count(problemCasesPath, isAllInputCaseInOneFile):
    caseCount = len(glob.glob(os.path.join(problemCasesPath, '*.*')))/2
    
    if caseCount > 1:
        if isAllInputCaseInOneFile == ENUMResources.const.FALSE:
            caseCount -= 1
        else:
            caseCount = 1

def get_old_submitted_files(memberId, problemId, courseId):
    try:
        oldSubmittedFiles = dao.query(SubmittedFiles).\
                            filter(and_(SubmittedFiles.memberId == memberId,
                                        SubmittedFiles.problemId == problemId,
                                        SubmittedFiles.courseId == courseId,
                                        SubmittedFiles.isDeleted == ENUMResources.const.FALSE))
    except Exception as e:
        return unknown_error('dbError')                            
    return oldSubmittedFiles

def get_submitted_files(memberId, problemId, courseId, fileIndex):
    getSubmittedFiles = dao.query(SubmittedFiles).\
                            filter(and_(SubmittedFiles.memberId == memberId,
                                        SubmittedFiles.problemId == problemId,
                                        SubmittedFiles.courseId == courseId,
                                        SubmittedFiles.fileIndex == fileIndex)).\
                            first()
    return getSubmittedFiles
    
def old_submitted_files_are_deleted(memberId, problemId, courseId):
    dao.query(SubmittedFiles).\
        filter(and_(SubmittedFiles.memberId == memberId,
                    SubmittedFiles.problemId == problemId,
                    SubmittedFiles.courseId == courseId,
                    SubmittedFiles.isDeleted == ENUMResources.const.FALSE)).\
        update(dict(isDeleted = ENUMResources.const.TRUE))  

def update_submitted_files(memberId, courseId, problemId, fileIndex, fileName, fileSize):
    dao.query(SubmittedFiles).\
        filter(and_(SubmittedFiles.memberId == memberId,
                    SubmittedFiles.problemId == problemId,
                    SubmittedFiles.courseId == courseId,
                    SubmittedFiles.fileIndex == fileIndex)).\
        update(dict(isDeleted = ENUMResources.const.FALSE,
                    fileName = fileName,
                    fileSize = fileSize))
                                          
@GradeServer.route('/problem_<courseId>_<problemId>', methods = ['POST'])
@login_required
def upload(courseId, problemId):
    memberId = session[SessionResources.const.MEMBER_ID]
    fileIndex = 1
    
    memberName = get_member_name(memberId)
    courseName = get_course_name(courseId)
    problemName = get_problem_name(problemId)
    
    makePath = MakePath(PATH, memberId, memberName, courseId, courseName, problemId, problemName)
    filePath = makePath.make_current_path()
    tempPath = makePath.make_temp_path()

    sumOfSubmittedFileSize = 0
    usedLanguage = 0
    usedLanguageVersion = 0

    try:
        os.mkdir(tempPath)
    except Exception as e:
        return unknown_error('askToMaster')
        
    try:
        oldSubmittedFiles = get_old_submitted_files(memberId, problemId, courseId)
        if oldSubmittedFiles != None:
            old_submitted_files_are_deleted(memberId, problemId, courseId)

        upload_files = request.files.getlist(OtherResources.const.GET_FILES)
        for file in upload_files:
            fileName = secure_filename(file.filename)
            try:
                file.save(os.path.join(tempPath, fileName))
            except Exception as e:
                errorCheck = ENUMResources.const.TRUE
            
            fileSize = os.stat(os.path.join(tempPath, fileName)).st_size 
            getSubmittedFiles = get_submitted_files(memberId, problemId, courseId, fileIndex)
            if getSubmittedFiles != None:                                         
                update_submitted_files(memberId, courseId, problemId, fileIndex, fileName, fileSize)
            else:
                insertSubmittedFilesObject = InsertToSubmittedFiles(memberId,
                                                                    courseId,
                                                                    problemId,
                                                                    fileIndex,
                                                                    fileName,
                                                                    filePath,
                                                                    fileSize)
                insert_submitted_files(insertSubmittedFilesObject)
            
            fileIndex += 1
            sumOfSubmittedFileSize += fileSize
    except Exception as e:
        dao.rollback()
        os.system("rm -rf %s" % tempPath)
        return unknown_error('askToMaster')
        
    dao.commit()
    os.system("rm -rf %s" % filePath)
    os.rename(tempPath, filePath)
    usedLanguageName = request.form[OtherResources.const.USED_LANGUAGE_NAME]
    usedLanguage = get_used_language(usedLanguageName)
    usedLanguageVersion = used_language_version(courseId, usedLanguage)
    subCountNum = get_submission_count(memberId, courseId, problemId)
    solCountNum = get_solution_check_count(memberId, courseId, problemId, subCountNum)
    insert_to_submissions(courseId, memberId, problemId, subCountNum, solCountNum, usedLanguage, sumOfSubmittedFileSize)
    problemPath, limitedTime, limitedMemory, solutionCheckType, problemCasesPath = get_problem_info(problemId, problemName)
    isAllInputCaseInOneFile = is_support_multiple_case(problemId, courseId)
    
    caseCount = get_case_count(problemCasesPath, isAllInputCaseInOneFile)
    problemIdName = '%s_%s' %(problemId, problemName)
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
                   subCountNum,
                   problemIdName)
    
    flash(OtherResources.const.SUBMISSION_SUCCESS)
    
    return "0"

@GradeServer.route('/problem_<courseId>_page<pageNum>_<problemId>', methods = ['POST'])
@login_required
def code(courseId, pageNum, problemId):
    memberId = session[SessionResources.const.MEMBER_ID]
    fileIndex = 1
    usedLanguage = 0
    usedLanguageVersion = 0
    
    memberName = get_member_name(memberId)
    courseName = get_course_name(courseId)
    problemName = get_problem_name(problemId)
    
    makePath = MakePath(PATH, memberId, memberName, courseId, courseName, problemId, problemName)
    filePath = makePath.make_current_path()
    tempPath = makePath.make_temp_path()
    
    try:
        os.mkdir(tempPath)
    except Exception as e:
        return unknown_error('askToMaster')
    
    tests = request.form[OtherResources.const.GET_CODE]
    unicode(tests)
    tests = tests.replace(OtherResources.const.LINUX_NEW_LINE, OtherResources.const.WINDOWS_NEW_LINE)
    usedLanguageName = request.form[OtherResources.const.LANGUAGE]
    
    if usedLanguageName == OtherResources.const.C:
        fileName = OtherResources.const.C_SOURCE_NAME
    
    elif usedLanguageName == OtherResources.const.CPP:
        fileName = OtherResources.const.CPP_SOURCE_NAME
    
    elif usedLanguageName == OtherResources.const.JAVA:
        className = re.search(OtherResources.const.JAVA_MAIN_CLASS, tests)
        try:
            fileName = OtherResources.const.JAVA_SOURCE_NAME %(className.group(1))
        except:
            fileName = OtherResources.const.MISS_CLASS_NAME
        
    elif usedLanguageName == OtherResources.const.PYTHON:
        fileName = OtherResources.const.PYTHON_SOURCE_NAME
        
    try:
        fout = open(os.path.join(tempPath, fileName), 'w')
        fout.write(tests)
        fout.close()
    except:
        os.system("rm -rf %s" % tempPath)
        return unknown_error('fileSaveError')

    os.system("rm -rf %s" % filePath)
    os.rename(tempPath, filePath)
    fileSize = os.stat(os.path.join(filePath, fileName)).st_size
    
    try:
        oldSubmittedFiles = get_old_submitted_files(memberId, problemId, courseId)
        if oldSubmittedFiles != None:
            old_submitted_files_are_deleted(memberId, problemId, courseId)
        getSubmittedFiles = get_submitted_files(memberId, problemId, courseId, fileIndex)
        if getSubmittedFiles != None:                                         
            update_submitted_files(memberId, courseId, problemId, fileIndex, fileName, fileSize)
        else:
            insertSubmittedFilesObject = InsertToSubmittedFiles(memberId, courseId, problemId, fileIndex, fileName, filePath, fileSize)
            insert_submitted_files(insertSubmittedFilesObject)
    except Exception as e:
        dao.rollback()
        return unknown_error('dbError') 
    dao.commit()

    usedLanguage = get_used_language(usedLanguageName)
    usedLanguageVersion = used_language_version(courseId, usedLanguage)
    subCountNum = get_submission_count(memberId, courseId, problemId)
    solCountNum = get_solution_check_count(memberId, courseId, problemId, subCountNum)
    insert_to_submissions(courseId, memberId, problemId, subCountNum, solCountNum, usedLanguage, sumOfSubmittedFileSize)
    problemPath, limitedTime, limitedMemory, solutionCheckType, problemCasesPath = get_problem_info(problemId, problemName)

    isAllInputCaseInOneFile = is_support_multiple_case(problemId, courseId)
    
    caseCount = get_case_count(problemCasesPath, isAllInputCaseInOneFile)
        
    problemIdName = '%s_%s' %(problemId, problemName)
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
                   subCountNum,
                   problemIdName)
    
    flash(OtherResources.const.SUBMISSION_SUCCESS)
    return redirect(url_for(RouteResources.const.PROBLEM_LIST,
                            courseId = courseId,
                            pageNum = pageNum))
    
def insert_to_submissions(courseId, memberId, problemId, subCountNum, solCountNum, usedLanguage, sumOfSubmittedFileSize):
    try:
        submissions = Submissions(memberId = memberId,
                                  problemId = problemId,
                                  courseId = courseId,
                                  submissionCount = subCountNum,
                                  solutionCheckCount = solCountNum,
                                  status = ENUMResources.const.JUDGING,
                                  codeSubmissionDate = datetime.now(),
                                  sumOfSubmittedFileSize = sumOfSubmittedFileSize,
                                  usedLanguage = usedLanguage)
        dao.add(submissions)
        
    except Exception as e:
        dao.rollback()
        return unknown_error('dbError')
    dao.commit()
    """try:
        departmentIndex = dao.query(DepartmentsDetailsOfMembers.departmentIndex).\
                              filter(DepartmentsDetailsOfMembers.memberId == memberId).\
                              first().\
                              departmentIndex
    except Exception as e:
        return unknown_error('dbError')"""
        
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
                   subCountNum,
                   problemIdName): 
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
                subCountNum,
                problemIdName)