# -*- coding: utf-8 -*-

from flask import request, redirect, session, url_for, render_template, flash
from sqlalchemy import and_, func

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils.loginRequired import login_required
from GradeServer.model.registeredProblems import RegisteredProblems
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.problems import Problems
from GradeServer.model.submissions import Submissions
from GradeServer.model.submittedRecordsOfProblems import SubmittedRecordsOfProblems
from GradeServer.model.languages import Languages
from GradeServer.model.languagesOfCourses import LanguagesOfCourses

@GradeServer.route('/problemList/<courseId>')
@login_required
def problemList(courseId):
    """ problem submitting page """
    course = []
    problems = []
    try:
        submissionRecords = dao.query(Submissions).\
                                filter(Submissions.memberId == session['memberId']).\
                                order_by(Submissions.problemId.desc(),
                                         Submissions.courseId.desc()).\
                                group_by(Submissions.problemId,
                                         Submissions.courseId).subquery()
    except:
        print 'failed submissionRecords'
    try:
        problems = dao.query(RegisteredProblems).\
                       outerjoin(submissionRecords,
                                 and_(submissionRecords.c.problemId == RegisteredProblems.problemId,
                                      submissionRecords.c.courseId == RegisteredProblems.courseId)).\
                                      filter(RegisteredProblems.courseId == courseId).subquery()
    except:
        print 'failed problems'
    try:
        problems = dao.query(problems,
                             Problems.problemName).\
                       join(Problems,
                            Problems.problemId == problems.c.problemId).all()
    except:
        print 'failed problems2'
    try:
        course = dao.query(RegisteredCourses).filter_by(courseId=courseId).first()
    except:
        print 'failed course'
    
    return render_template('/problem_list.html',
                           course = course,
                           problems = problems)

@GradeServer.route('/problem/<courseId>/<problemId>')
@login_required
def problem(courseId, problemId):
    """
    use db to get its problem page
    now, it moves to just default problem page
    """
    try:
        languageName = dao.query(Languages.languageName).\
                           join(LanguagesOfCourses, 
                                and_(Languages.languageIndex == LanguagesOfCourses.languageIndex,
                                Languages.languageVersion == LanguagesOfCourses.languageVersion)).\
                                filter(LanguagesOfCourses.courseId == courseId).all()
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise 
    try:
        languageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                              filter(LanguagesOfCourses.courseId == courseId).all()
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise 
    try:
        languageIndex = dao.query(LanguagesOfCourses.languageIndex).\
                            filter(LanguagesOfCourses.courseId == courseId).all()
    except Exception as e:
        dao.rollback()
        print 'DB error : ' + str(e)
        raise 

    problemInformation = dao.query(Problems).\
                             filter(Problems.problemId == problemId).first()
                             
    return render_template('/problem.html',
                           courseId = courseId,
                           problemId = problemId,
                           problemInformation = problemInformation,
                           languageName = languageName,
                           languageVersion = languageVersion,
                           languageIndex = languageIndex)

"""
    in the main page, it uses methods so 
    before login, need to block to access to other menus
"""
        
@GradeServer.route('/problem', methods=['GET', 'POST'])
@login_required
def submit():
    """ 
    when user pushed submit button
    """
    """
    error = None
    if request.method == 'POST':
        # if user doesn't upload any file or write any code
        error = "add your source file or write your source code"
    """
    return render_template('/result.html')

@GradeServer.route('/record/<courseId>/<problemId>')
@login_required
def record(courseId, problemId):
    """
    navbar - class - Record of problem
    """
    try:
        submittedRecords = dao.query(SubmittedRecordsOfProblems).\
                               filter_by(problemId=problemId).\
                               filter_by(courseId=courseId).all()
    except:
        print 'SubmittedRecordsOfProblems table is empty'
        submittedRecords = []
    
    problemInformation = dao.query(Problems).\
                             filter(Problems.problemId == problemId).first()
    return render_template('/record.html',
                           submittedRecords = submittedRecords,
                           problemInformation = problemInformation)

@GradeServer.route('/problem/userid')
@login_required
def user_record():
    return render_template('/user_code.html')