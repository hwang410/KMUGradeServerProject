#-*- coding: utf-8 -*-

import os
import sys
import shutil
import glob
import re

from flask import Flask, request, redirect, url_for, session, flash
from werkzeug import secure_filename

from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils.loginRequired import login_required
from GradeServer.GradeServer_config import GradeServerConfig
from GradeServer.utils.utilCodeSubmissionQuery import get_member_name, get_course_name, get_submission_count, \
                                                      insert_submitted_files, get_used_language_index, insert_to_submissions, \
                                                      get_problem_info, get_used_language_version, delete_submitted_files_data
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.checkInvalidAccess import check_invalid_access
from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.routeResources import RouteResources
from sqlalchemy import and_, func, update
from GradeServer.celeryServer import Grade

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

def get_case_count(problemCasesPath, isAllInputCaseInOneFile):
    caseCount = len(glob.glob(os.path.join(problemCasesPath, '*.*')))/2
    
    if caseCount > 1:
        if isAllInputCaseInOneFile == ENUMResources.const.FALSE:
            caseCount -= 1
        else:
            caseCount = 1
    return caseCount

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
        
def send_to_celery_and_insert_to_submissions(memberId, courseId, problemId, usedLanguageName, sumOfSubmittedFileSize, problemName, filePath, tempPath):
    try:
        usedLanguageIndex = get_used_language_index(usedLanguageName)
        usedLanguageVersion = get_used_language_version(courseId, usedLanguageIndex)
        subCountNum = get_submission_count(memberId, courseId, problemId)
        insert_to_submissions(courseId, memberId, problemId, usedLanguageIndex, subCountNum, sumOfSubmittedFileSize)
        problemPath, limitedTime, limitedMemory, solutionCheckType, isAllInputCaseInOneFile, numberOfTestCase, problemCasesPath = get_problem_info(problemId, problemName)
        problemFullName = make_problem_full_name(problemId, problemName)
        
        Grade.delay(str(filePath),
                    str(problemPath),
                    str(memberId),
                    str(problemId),
                    str(solutionCheckType),
                    numberOfTestCase,
                    limitedTime,
                    limitedMemory,
                    str(usedLanguageName),
                    str(usedLanguageVersion),
                    str(courseId),
                    subCountNum,
                    str(problemFullName))

                       
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
@check_invalid_access
@login_required
def to_process_uploaded_files(courseId, problemId, problemName):
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
@check_invalid_access
@login_required
def to_process_written_code(courseId, pageNum, problemId, problemName):
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
