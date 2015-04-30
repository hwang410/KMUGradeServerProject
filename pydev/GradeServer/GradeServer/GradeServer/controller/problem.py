# -*- coding: utf-8 -*-

from flask import request, redirect, session, url_for, render_template, flash
from sqlalchemy import and_, func

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilQuery import select_submission_people_count, select_solved_people_count, select_count
from GradeServer.utils.utilSubmissionQuery import submissions_sorted, select_last_submissions, select_all_submission
from GradeServer.utils.utilMessages import unknown_error

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer

from GradeServer.model.registeredProblems import RegisteredProblems
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.problems import Problems
from GradeServer.model.submissions import Submissions
from GradeServer.model.submittedFiles import SubmittedFiles
from GradeServer.model.submittedRecordsOfProblems import SubmittedRecordsOfProblems
from GradeServer.model.languages import Languages
from GradeServer.model.languagesOfCourses import LanguagesOfCourses
from itertools import count


@GradeServer.route('/problemList/<courseId>/page<pageNum>')
@login_required
def problemList(courseId, pageNum):
    """ problem submitting page """
    # Get Last Submitted History
    lastSubmission = select_last_submissions(memberId = session[SessionResources().const.MEMBER_ID],
                                             courseId = courseId).subquery()
    # Current Submission                                      
    submissions = dao.query(Submissions.score,
                            Submissions.status,
                            lastSubmission).\
                      join(lastSubmission,
                           and_(Submissions.memberId == lastSubmission.c.memberId,
                                Submissions.problemId == lastSubmission.c.problemId,
                                Submissions.courseId == lastSubmission.c.courseId,
                                Submissions.solutionCheckCount == lastSubmission.c.solutionCheckCount)).\
                      subquery()
    
    # Get Problem Informations
    problems = dao.query(RegisteredProblems.problemId,
                         RegisteredProblems.startDateOfSubmission,
                         RegisteredProblems.endDateOfSubmission,
                         Problems.problemName).\
                   filter(RegisteredProblems.courseId == courseId).\
                   join(Problems,
                        RegisteredProblems.problemId == Problems.problemId).\
                   subquery()
    # Get ProblemList Count
    try:
        count = select_count(problems.c.problemId).first().\
                                                   count
    except Exception:
        count = 0
    # Get ProblemListRecords OuterJoin
    try:
        problemListRecords = get_page_record(dao.query(problems,
                                                       submissions.c.score,
                                                       submissions.c.status,
                                                       submissions.c.solutionCheckCount).\
                                                 outerjoin(submissions,
                                                           problems.c.problemId == submissions.c.problemId).\
                                                 order_by(problems.c.startDateOfSubmission.desc()),
                                             pageNum = int(pageNum)).all()
    except Exception:
        problemListRecords = []
        
    # Get Course Information
    try:
        courseRecords = dao.query(RegisteredCourses.courseId,
                                  RegisteredCourses.courseName).\
                            filter(RegisteredCourses.courseId == courseId).\
                            first()
    except:
        courseRecords = []
    
    return render_template(HTMLResources().const.PROBLEM_LIST_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           courseRecords = courseRecords,
                           problemListRecords = problemListRecords,
                           pages = get_page_pointed(pageNum = int(pageNum),
                                                   count = count))

@GradeServer.route('/problem/<courseId>/<problemId>?page<pageNum>')
@login_required
def problem(courseId, problemId, pageNum):
    """
    use db to get its problem page
    now, it moves to just default problem page
    """
    try:
        languageName = dao.query(Languages.languageName).\
                           join(LanguagesOfCourses, 
                                Languages.languageIndex == LanguagesOfCourses.languageIndex).\
                           filter(LanguagesOfCourses.courseId == courseId).\
                           all()
    except Exception as e:
        unknown_error("DB 에러입니다")
    try:
        languageVersion = dao.query(Languages.languageVersion).\
                              join(LanguagesOfCourses,
                                   and_(LanguagesOfCourses.courseId == courseId,
                                        LanguagesOfCourses.languageIndex == Languages.languageIndex)).\
                              all()
    except Exception as e:
        unknown_error("DB 에러입니다") 
    try:
        languageIndex = dao.query(LanguagesOfCourses.languageIndex).\
                            filter(LanguagesOfCourses.courseId == courseId).\
                            all()
    except Exception as e:
        unknown_error("DB 에러입니다")
        
    try:
        problemInformation = dao.query(Problems).\
                             filter(Problems.problemId == problemId).\
                             first()
    except Exception as e:
        unknown_error("DB 에러입니다")       
    
    problemName = problemInformation.problemName.replace(' ', '')
    browserName = request.user_agent.browser
    
    return render_template(HTMLResources().const.PROBLEM_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           courseId = courseId,
                           problemId = problemId,
                           problemInformation = problemInformation,
                           problemName = problemName,
                           languageName = languageName,
                           languageVersion = languageVersion,
                           languageIndex = languageIndex,
                           pageNum = pageNum,
                           browserName = browserName)

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

@GradeServer.route('/record/<courseId>/<problemId>-<sortCondition>')
@login_required
def problem_record(courseId, problemId, sortCondition = OtherResources().const.RUN_TIME):
    """
    navbar - class - Record of problem
    """
    # Chart View Value Text
    chartSubmissionDescriptions = ['Total Submitted People',
                                   'Total Solved People',
                                   'Total Submitted Count',
                                   'Solved',
                                   'Wrong Answer',
                                   'Time Over',
                                   'Compile Error',
                                   'RunTime Error']
    
    # last Submissions Info
    submissions = select_all_submission(lastSubmission = select_last_submissions(memberId = None,
                                                                                 courseId = courseId,
                                                                                 problemId = problemId).subquery(),
                                        memberId = None,
                                        courseId = courseId,
                                        problemId = problemId).subquery()
    try:
        # Submitted Members Count
        sumOfSubmissionPeopleCount = select_submission_people_count(submissions).subquery()
        # Solved Members Count
        sumOfSolvedPeopleCount = select_solved_people_count(submissions).subquery()
        # Problem Rrecord
        problemSubmittedRecords = dao.query(SubmittedRecordsOfProblems.sumOfSubmissionCount,
                                            SubmittedRecordsOfProblems.sumOfSolvedCount,
                                            SubmittedRecordsOfProblems.sumOfWrongCount,
                                            SubmittedRecordsOfProblems.sumOfTimeOverCount,
                                            SubmittedRecordsOfProblems.sumOfCompileErrorCount,
                                            SubmittedRecordsOfProblems.sumOfRuntimeErrorCount).\
                                      filter(SubmittedRecordsOfProblems.problemId == problemId,
                                             SubmittedRecordsOfProblems.courseId == courseId).\
                                      subquery()
        # Chart SubmissionRecords
        chartSubmissionRecords = dao.query(sumOfSubmissionPeopleCount,
                                           sumOfSolvedPeopleCount,
                                           problemSubmittedRecords).\
                                     first()
    except:
        print 'SubmittedRecordsOfProblems table is empty'
        chartSubmissionRecords = []
        
    # Problem Information (LimitedTime, LimitedMemory
    try:
        problemInformationRecords = dao.query(Problems.problemId,
                                              Problems.problemName,
                                              Problems.limitedTime,
                                              Problems.limitedMemory).\
                                        filter(Problems.problemId == problemId).\
                                        first()
    except Exception:
        problemInformationRecords = []
    # Problem Solved Users
    try:
       # Problem Solved Member
        problemSolvedMemberRecords = submissions_sorted(dao.query(submissions).\
                                                            filter(submissions.c.status == ENUMResources().const.SOLVED).\
                                                            subquery(),
                                                        sortCondition = sortCondition).all()
            
    except Exception:
        problemSolvedMemberRecords = []
    
    return render_template(HTMLResources().const.PROBLEM_RECORD_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           courseId = courseId,
                           problemSolvedMemberRecords = problemSolvedMemberRecords,
                           problemInformationRecords = problemInformationRecords,
                           chartSubmissionDescriptions = chartSubmissionDescriptions,
                           chartSubmissionRecords = chartSubmissionRecords)

@GradeServer.route('/problem/<courseId>/<problemId>')
@login_required
def submission_code(courseId, problemId):
    
    # are Not an Administrator and endOfSubmission ago
    if SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]\
       or SETResources().const.COURSE_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]:
        # Problem Information (LimitedTime, LimitedMemory
        try:
            problemName = dao.query(Problems.problemName).\
                                    filter(Problems.problemId == problemId).\
                                    first().\
                                    problemName
        except Exception:
            problemName = None
            
        # Problem Solved Users
        try:
            # last Submissions Info
            submissions = select_all_submission(lastSubmission = select_last_submissions(memberId = session[SessionResources().const.MEMBER_ID],
                                                                                         courseId = courseId,
                                                                                         problemId = problemId).subquery(),
                                                memberId = session[SessionResources().const.MEMBER_ID],
                                                courseId = courseId,
                                                problemId = problemId).subquery()
            problemSolvedMemberRecords = dao.query(submissions).\
                                             filter(submissions.c.status == ENUMResources().const.SOLVED).\
                                             first()
        except Exception:
            problemSolvedMemberRecords = []
            
        # Submitted Files Information
        try:
            submittedFileRecords = dao.query(SubmittedFiles.fileName,
                                             SubmittedFiles.filePath).\
                                       filter(SubmittedFiles.memberId == session[SessionResources().const.MEMBER_ID],
                                              SubmittedFiles.problemId == problemId,
                                              SubmittedFiles.courseId == courseId).\
                                       all()
            fileData = []
            for raw in submittedFileRecords:
                # Open
                filePath = raw.filePath + '/' +raw.fileName
                file = open(filePath)
                
                # Read
                data = file.read()
                
                # Close
                file.close()
                fileData.append(data)
        except Exception:
            submittedFileRecords = []
            fileData = []
       
        return render_template(HTMLResources().const.SUBMISSION_CODE_HTML,
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               submittedFileRecords = submittedFileRecords,
                               fileData = fileData,
                               problemName = problemName,
                               problemSolvedMemberRecords = problemSolvedMemberRecords)