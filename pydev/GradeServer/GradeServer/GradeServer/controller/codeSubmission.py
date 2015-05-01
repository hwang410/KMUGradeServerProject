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
from GradeServer.utils.utilMessages import get_message

# Initialize the Flask application
PATH = GradeServerConfig.CURRENT_FOLDER

def make_path(PATH, memberId, courseId, problemId, problemName):
    memberName = get_member_name(memberId)
    courseName = get_course_name(courseId)
    filePath = '%s/%s_%s/%s_%s/%s_%s' %(PATH, courseId, courseName, memberId, memberName, problemId, problemName)
    tempPath = '%s/%s_%s/%s_%s/%s_%s_tmp' %(PATH, courseId, courseName, memberId, memberName, problemId, problemName)
    return filePath.replace(' ', ''), tempPath.replace(' ', '')

def make_problem_full_name(problemId, problemName):
    return '%s_%s' %(problemId, problemName)
        
def get_course_name(courseId):
    try:
        courseName = dao.query(RegisteredCourses.courseName).\
                         filter(RegisteredCourses.courseId == courseId).\
                         first().\
                         courseName
        return courseName
    except Exception as e:
        return unknown_error(get_message('dbError'))
    
def get_problem_name(problemId):
    try:
        problemName = dao.query(Problems.problemName).\
                          filter(Problems.problemId == problemId).\
                          first().\
                          problemName
        return problemName
    except Exception as e:
        return unknown_error(get_message('dbError'))

def get_member_name(memberId):
    try:
        memberName = dao.query(Members.memberName).\
                         filter(Members.memberId == memberId).\
                         first().\
                         memberName
        return memberName
    except Exception as e:
        return unknown_error(get_message('dbError'))

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

def insert_submitted_files(memberId, courseId, problemId, fileIndex, fileName, filePath, fileSize):
    submittedFiles = SubmittedFiles(memberId = memberId,
                                    courseId = courseId,
                                    problemId = problemId,
                                    fileIndex = fileIndex,
                                    fileName = fileName,
                                    filePath = filePath,
                                    fileSize = fileSize)                
    dao.add(submittedFiles)
    
def get_used_language_index(usedLanguageName):
    try:
        usedLanguageIndex = dao.query(Languages.languageIndex).\
                           filter(Languages.languageName == usedLanguageName).\
                           first().\
                           languageIndex
    except Exception as e:
        return unknown_error(get_message('dbError'))
    return usedLanguageIndex

def get_problem_info(problemId, problemName):
    try:
        problemPath, limitedTime, limitedMemory, solutionCheckType, isAllInputCaseInOneFile = dao.query(Problems.problemPath,
                                                                                                        Problems.limitedTime,
                                                                                                        Problems.limitedMemory,
                                                                                                        Problems.solutionCheckType,
                                                                                                        RegisteredProblems.isAllInputCaseInOneFile).\
                                                                                                  join(RegisteredProblems, Problems.problemId == RegisteredProblems.problemId).\
                                                                                                        filter(Problems.problemId == problemId).\
                                                                         first()
        problemCasesPath = '%s/%s_%s_%s' %(problemPath, problemId, problemName, solutionCheckType)
    except Exception as e:
        return unknown_error(get_message('dbError'))
    return problemPath, limitedTime, limitedMemory, solutionCheckType, isAllInputCaseInOneFile, problemCasesPath

def used_language_version(courseId, usedLanguage):
    try:
        usedLanguageVersion = dao.query(Languages.languageVersion).\
                                  join(LanguagesOfCourses, LanguagesOfCourses.languageIndex == Languages.languageIndex).\
                                  filter(LanguagesOfCourses.courseId == courseId,
                                         LanguagesOfCourses.languageIndex == usedLanguage).\
                                  first().\
                                  languageVersion
    except Exception as e:
        return unknown_error(get_message('dbError'))
    return usedLanguageVersion

def get_case_count(problemCasesPath, isAllInputCaseInOneFile):
    caseCount = len(glob.glob(os.path.join(problemCasesPath, '*.*')))/2
    
    if caseCount > 1:
        if isAllInputCaseInOneFile == ENUMResources.const.FALSE:
            caseCount -= 1
        else:
            caseCount = 1
    return caseCount

def delete_submitted_files_data(memberId, problemId, courseId):
    deleteData = dao.query(SubmittedFiles).\
                     filter(and_(SubmittedFiles.memberId == memberId,
                                 SubmittedFiles.problemId == problemId,
                                 SubmittedFiles.courseId == courseId)).\
                     delete()
def file_save_with_insert_to_SubmittedFiles(memberId, courseId, problemId, uploadFiles, tempPath, filePath):
    fileIndex = 1
    try:
        sumOfSubmittedFileSize = 0
        delete_submitted_files_data(memberId, problemId, courseId)
        for file in uploadFiles:
            fileName = secure_filename(file.filename)
            try:
                file.save(os.path.join(tempPath, fileName))
            except Exception as e:
                flash(get_message('fileSaveError'))
                return "0"
            
            fileSize = os.stat(os.path.join(tempPath, fileName)).st_size
            insert_submitted_files(memberId, courseId, problemId, fileIndex, fileName, filePath, fileSize)
            fileIndex += 1
            sumOfSubmittedFileSize += fileSize
    except Exception as e:
        dao.rollback()
        os.system("rm -rf %s" % tempPath)
        flash(get_message('askToMaster'))
        return "0"
    
    return sumOfSubmittedFileSize

def insert_to_submissions(courseId, memberId, problemId, usedLanguageIndex, subCountNum, sumOfSubmittedFileSize):
    solCountNum = get_solution_check_count(memberId, courseId, problemId, subCountNum)
    submissions = Submissions(memberId = memberId,
                              problemId = problemId,
                              courseId = courseId,
                              submissionCount = subCountNum,
                              solutionCheckCount = solCountNum,
                              status = ENUMResources.const.JUDGING,
                              codeSubmissionDate = datetime.now(),
                              sumOfSubmittedFileSize = sumOfSubmittedFileSize,
                              usedLanguageIndex = usedLanguageIndex)
    dao.add(submissions)
        
def send_to_celery_and_insert_to_submissions(memberId, courseId, problemId, usedLanguageName, sumOfSubmittedFileSize, problemName, filePath, tempPath):
    try:
        usedLanguageIndex = get_used_language_index(usedLanguageName)
        usedLanguageVersion = used_language_version(courseId, usedLanguageIndex)
        subCountNum = get_submission_count(memberId, courseId, problemId)
        insert_to_submissions(courseId, memberId, problemId, usedLanguageIndex, subCountNum, sumOfSubmittedFileSize)
        problemPath, limitedTime, limitedMemory, solutionCheckType, isAllInputCaseInOneFile, problemCasesPath = get_problem_info(problemId, problemName)
        caseCount = get_case_count(problemCasesPath, isAllInputCaseInOneFile)
        problemFullName = make_problem_full_name(problemId, problemName)


        """Grade.delay(str(filePath),
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
                str(problemFullName))"""

                       
        flash(OtherResources.const.SUBMISSION_SUCCESS)
        dao.commit()
    except Exception as e:
        dao.rollback()
        os.system("rm -rf %s" % tempPath)
        return unknown_error(get_message('dbError'))
    os.system("rm -rf %s" % filePath)
    os.rename(tempPath, filePath)
    
def get_language_name(usedLanguageName, tests):
    if usedLanguageName == OtherResources.const.C:
        languageName = OtherResources.const.C_SOURCE_NAME

    if usedLanguageName == OtherResources.const.CPP:
        languageName = OtherResources.const.CPP_SOURCE_NAME

    if usedLanguageName == OtherResources.const.JAVA:
        className = re.search(OtherResources.const.JAVA_MAIN_CLASS, tests)
        try:
            languageName = OtherResources.const.JAVA_SOURCE_NAME %(className.group(1))
        except:
            languageName = OtherResources.const.MISS_CLASS_NAME

    if usedLanguageName == OtherResources.const.PYTHON:
        languageName = OtherResources.const.PYTHON_SOURCE_NAME

    return languageName

def write_code_in_file(tempPath):
    tests = request.form[OtherResources.const.GET_CODE]
    unicode(tests)
    tests = tests.replace(OtherResources.const.LINUX_NEW_LINE, OtherResources.const.WINDOWS_NEW_LINE)
    usedLanguageName = request.form[OtherResources.const.LANGUAGE]
    
    fileName = get_language_name(usedLanguageName, tests)
    try:
        fout = open(os.path.join(tempPath, fileName), 'w')
        fout.write(tests)
        fout.close()
    except:
        os.system("rm -rf %s" % tempPath)
        return unknown_error(get_message('fileSaveError'))
    return usedLanguageName, fileName
@GradeServer.route('/problem_<courseId>_<problemId>_<problemName>', methods = ['POST'])
@login_required
def upload(courseId, problemId, problemName):
    memberId = session[SessionResources.const.MEMBER_ID]
    filePath, tempPath = make_path(PATH, memberId, courseId, problemId, problemName)
    try:
        os.mkdir(tempPath)
    except Exception as e:
        flash(get_message('askToMaster'))
        return "0"
      
    try:
        uploadFiles = request.files.getlist(OtherResources.const.GET_FILES)
        usedLanguageName = request.form[OtherResources.const.USED_LANGUAGE_NAME]
        sumOfSubmittedFileSize = file_save_with_insert_to_SubmittedFiles(memberId, courseId, problemId, uploadFiles, tempPath, filePath)
        send_to_celery_and_insert_to_submissions(memberId, courseId, problemId, usedLanguageName, sumOfSubmittedFileSize, problemName, filePath, tempPath)
    except:
        os.system("rm -rf %s" % tempPath)
        return unknown_error(get_message('askToMaster'))        
    return "0"

@GradeServer.route('/problem_<courseId>_page<pageNum>_<problemId>_<problemName>', methods = ['POST'])
@login_required
def code(courseId, pageNum, problemId, problemName):
    memberId = session[SessionResources.const.MEMBER_ID]
    filePath, tempPath = make_path(PATH, memberId, courseId, problemId, problemName)
    try:
        os.mkdir(tempPath)
    except Exception as e:
        return unknown_error(get_message('askToMaster'))
    
    try:
        usedLanguageName, fileName = write_code_in_file(tempPath)
        fileSize = os.stat(os.path.join(tempPath, fileName)).st_size
        fileIndex = 1
        delete_submitted_files_data(memberId, problemId, courseId)
        insert_submitted_files(memberId, courseId, problemId, fileIndex, fileName, filePath, fileSize)
        send_to_celery_and_insert_to_submissions(memberId, courseId, problemId, usedLanguageName, fileSize, problemName, filePath, tempPath)
    except:
        os.system("rm -rf %s" % tempPath)
        return unknown_error(get_message('askToMaster'))
    return redirect(url_for(RouteResources.const.PROBLEM_LIST,
                            courseId = courseId,
                            pageNum = pageNum))
