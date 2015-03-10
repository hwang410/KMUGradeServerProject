#-*- coding: utf-8 -*-

import os
import sys
#from GradeServer.controller import codesubmission

reload(sys)
#sys.setdefaultencoding('utf-8')

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, make_response, \
current_app, session, flash
from werkzeug import secure_filename
from datetime import datetime
import uuid
from wtforms import Form, FileField, TextField, TextAreaField, HiddenField, validators

from GradeServer.database import dao
#from GradeServer.model.recordsOfFileSubmit import SubmitFileRecord
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.controller.login import login_required
from GradeServer.controller.problem import *
from GradeServer.model.members import Members
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.problems import Problems
from GradeServer.model.submittedFiles import SubmittedFiles
from GradeServer.model.submissions import Submissions
from GradeServer.model.languages import Languages
from GradeServer.model.languagesOfCourses import LanguagesOfCourses
from GradeServer.GradeServer_config import GradeServerConfig
from sqlalchemy import and_, func
from datetime import datetime

# Initialize the Flask application
ALLOWED_EXTENSIONS = set(['py', 'java', 'class', 'c', 'cpp', 'h', 'jar'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@GradeServer.route('/problem/<courseId>/<problemId>/upload', methods = ['POST'])
@login_required
def upload(courseId, problemId):
    memberId = session['memberId']
    fileIndex = 1
    courseName = dao.query(RegisteredCourses.courseName).filter_by(courseId = courseId).first()
    problemName = dao.query(Problems.problemName).filter_by(problemId = problemId).first()
    filePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s/%s' %(courseId, courseName[0], problemId, problemName[0], memberId)
    #storePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s' %(courseId, courseName[0], problemId, problemName[0])
    upload_files = request.files.getlist('file[]')
    filenames = []
    sumOfSubmittedFileSize = 0
    uLang = 1
    uVersion = 0
 
    a =dao.query (Submissions.memberId).all ()
    for raw in a :
        print raw.memberId, "CCCC"
    try:
        dao.query(SubmittedFiles).filter(and_(SubmittedFiles.memberId == memberId, SubmittedFiles.problemId == problemId,
                                              SubmittedFiles.courseId == courseId)).delete()
        dao.commit()
    except Exception as e:
        
        print "DB error : " + str(e)
        raise e 
    
    a =dao.query (Submissions.memberId).all ()
    for raw in a :
        print raw.memberId, "BBBB"

    for file in upload_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(filePath, filename))
            fileSize = os.stat(filePath + '/' + filename).st_size
            filenames.append(filename)
            
            
            if filename.rsplit('.', 1)[1] == 'c':
                uLang = dao.query(Languages.languageIndex).filter_by(languageName = 'C').first()
            elif filename.rsplit('.', 1)[1] == 'cpp':
                uLang = dao.query(Languages.languageIndex).filter_by(languageName = 'C++').first()                                                                    
            elif filename.rsplit('.', 1)[1] == 'java':
                uLang = dao.query(Languages.languageIndex).filter_by(languageName = 'JAVA').first()
            elif filename.rsplit('.', 1)[1] == 'py':
                uLang = dao.query(Languages.languageIndex).filter_by(languageName = 'PYTHON').first()
                                                                     
                              
            try:
                ufile = SubmittedFiles(memberId = memberId, problemId = problemId, courseId = courseId , fileIndex = fileIndex, fileName = filename,
                                        filePath = filePath, fileSize = fileSize)                
                dao.add(ufile)
                dao.commit()
                                   
            except Exception as e:
                dao.rollback()
                print "DB error : " + str(e)
                raise e            
            fileIndex += 1
            sumOfSubmittedFileSize += fileSize
    a =dao.query (Submissions.memberId).all ()
    for raw in a :
        print raw.memberId, "AAAA"
    uVersion = dao.query(LanguagesOfCourses.languageVersion).filter_by(courseId = courseId).first()
    print "AAAAA"
    print courseId, problemId, memberId
    try:
        print "CCCC"
        subCount = dao.query(func.max (Submissions.submissionCount).label ("submissionCount")).filter(Submissions.memberId == memberId, Submissions.courseId == courseId,
                   Submissions.problemId == int (problemId)).first()
        print "BBBB", subCount.submissionCount
        subCountNum = subCount.submissionCount + 1
        print "DDDD"
        solCountNum = subCountNum
    except:
        print "AAAA"
        subCountNum = 1
        solCountNum = 0
        
    """try:
        solCount = dao.query(Submissions.solutionCheckCount).filter(and_(Submissions.memberId == memberId, Submissions.courseId == courseId,
                    Submissions.problemId == problemId))
        solCountNum = solCount[0] + 1
    except:
        solCountNum = 1"""
    
    try:
        sub = Submissions(memberId = memberId, problemId = int (problemId), courseId = courseId, submissionCount = subCountNum, solutionCheckCount = solCountNum, codeSubmissionDate = datetime.now(),
                      sumOfSubmittedFileSize = sumOfSubmittedFileSize, usedLanguage = uLang[0], usedLanguageVersion = uVersion[0])
        dao.add(sub)
        dao.commit()
    except Exception as e:
        print "DB error : " + str(e)
        raise e
          
    flash("submission success!")           
    return courseId
    #return redirect("./problemList/" + courseId)
    #return redirect(url_for('.problemList', courseId=courseId))
        
@GradeServer.route('/problem/<courseId>/<problemId>/codesubmission', methods = ['POST'])
@login_required
def code(courseId, problemId):
    
    memberId = session['memberId']
    fileIndex = 1
    courseName = dao.query(RegisteredCourses.courseName).filter_by(courseId = courseId).first()
    problemName = dao.query(Problems.problemName).filter_by(problemId = problemId).first()
    filePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s/%s' %(courseId, courseName[0], problemId, problemName[0], memberId)
    #storePath = '/mnt/shared/CurrentCourses/%s_%s/%s_%s' %(courseId, courseName[0], problemId, problemName[0])
    
    try:
         dao.query(SubmittedFiles).filter(and_(SubmittedFiles.memberId == memberId, SubmittedFiles.problemId == problemId,
        SubmittedFiles.courseId == courseId)).delete()
         dao.commit()
    except Exception as e:
        dao.rollback()
        print "DB error : " + str(e)
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
        fileSize = os.stat(filePath + '/' + filename).st_size
    
    elif num == '2':
        filename = 'test.cpp'
        fout = open(filePath + '/' + filename, 'w')
        fout.write(tests)
        fout.close()
        fileSize = os.stat(filePath + '/' + filename).st_size
    
    elif num == '3':
        filename = 'test.java'
        fout = open(filePath + '/' + filename, 'w')
        fout.write(tests)
        fout.close()
        fileSize = os.stat(filePath + '/' + filename).st_size
        
    elif num == '4':
        filename = 'test.py'
        fout = open(filePath + '/' + filename, 'w')
        fout.write(tests)
        fout.close()
        fileSize = os.stat(filePath + '/' + filename).st_size
        
    try:
        ufile = SubmittedFiles(memberId = memberId, problemId = problemId, courseId = courseId , fileIndex = fileIndex, fileName = filename,
                filePath = filePath, fileSize = fileSize)                
        dao.add(ufile)
        dao.commit()                
    except Exception as e:            
        dao.rollback()
        print "DB error : " + str(e)
        raise e
    
    flash("submission success!")
    return redirect (url_for('.problemList', courseId = courseId ))