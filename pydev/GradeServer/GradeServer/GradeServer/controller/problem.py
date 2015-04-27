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
    lastSubmissionCount = select_last_submissions(session[SessionResources.const.MEMBER_ID],
                                              courseId).subquery()
    # Current Submission                                      
    submissions = dao.query(Submissions.score,
                            Submissions.status,
                            lastSubmissionCount).\
                      join(lastSubmissionCount,
                           and_(Submissions.memberId == lastSubmissionCount.c.memberId,
                                Submissions.problemId == lastSubmissionCount.c.problemId,
                                Submissions.courseId == lastSubmissionCount.c.courseId,
                                Submissions.solutionCheckCount == lastSubmissionCount.c.solutionCheckCount)).\
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
                                                       submissions.c.status).\
                                                 outerjoin(submissions,
                                                           problems.c.problemId == submissions.c.problemId).\
                                                 order_by(problems.c.startDateOfSubmission.desc()),
                                             int(pageNum)).all()
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
    
    return render_template(HTMLResources.const.PROBLEM_LIST_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           courseRecords = courseRecords,
                           problemListRecords = problemListRecords,
                           pages = get_page_pointed(int(pageNum),
                                                   count))

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
                                and_(Languages.languageIndex == LanguagesOfCourses.languageIndex,
                                     Languages.languageVersion == LanguagesOfCourses.languageVersion)).\
                           filter(LanguagesOfCourses.courseId == courseId).\
                           all()
    except Exception as e:
        unknown_error("DB 에러입니다")
    try:
        languageVersion = dao.query(LanguagesOfCourses.languageVersion).\
                              filter(LanguagesOfCourses.courseId == courseId).\
                              all()
    except Exception as e:
        unknown_error("DB 에러입니filter(LanguagesOfCourses.courseId == courseId).\
                        다") 
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
    return render_template(HTMLResources.const.PROBLEM_HTML,
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
def record(courseId, problemId, sortCondition = OtherResources.const.RUN_TIME):
    """
    navbar - class - Record of problem
    """
    # Viiew Value Text
    chartSubmissionDescriptions = ['Total Submit People',
                                   'Total Solved People',
                                   'Total Submit Count',
                                   'Solved',
                                   'Wrong Answer',
                                   'Time Over',
                                   'Compile Error',
                                   'RunTime Error']
    try:
        submissions = select_all_submission(None, courseId, problemId).subquery()
        # Submitted Members Count
        sumOfSubmissionPeopleCount = select_submission_people_count(submissions).subquery()
        # Solved Members Count
        sumOfSolvedPeopleCount = select_solved_people_count(submissions).subquery()
                              
        problemSubmittedRecords = dao.query(func.max(SubmittedRecordsOfProblems.sumOfSubmissionCount).label('sumOfSubmissionCount'),
                                            func.max(SubmittedRecordsOfProblems.sumOfSolvedCount).label('sumOfSolvedCount'),
                                            func.max(SubmittedRecordsOfProblems.sumOfWrongCount).label('sumOfWrongCount'),
                                            func.max(SubmittedRecordsOfProblems.sumOfTimeOverCount).label('sumOfTimeOverCount'),
                                            func.max(SubmittedRecordsOfProblems.sumOfCompileErrorCount).label('sumOfCompileErrorCount'),
                                            func.max(SubmittedRecordsOfProblems.sumOfRuntimeErrorCount).label('sumOfRuntimeErrorCount')).\
                                      filter(SubmittedRecordsOfProblems.problemId == problemId,
                                             SubmittedRecordsOfProblems.courseId == courseId).\
                                      subquery()
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
        # last Submissions Info
        lastSubmissions = select_last_submissions(None, courseId, problemId).subquery()
       
       # Problem Solved Member
        problemSolvedMemberRecords = submissions_sorted(dao.query(submissions).\
                                                            filter(Submissions.status == ENUMResources.const.SOLVED).\
                                                            join(lastSubmissions,
                                                               and_(Submissions.memberId == submissions.c.memberId,
                                                                    Submissions.problemId == submissions.c.problemId,
                                                                    Submissions.courseId == submissions.c.courseId,
                                                                    Submissions.solutionCheckCount == submissions.c.solutionCheckCount)).\
                                                            subquery(),
                                                        sortCondition).all()
            
    except Exception:
        problemSolvedMemberRecords = []
    
    return render_template(HTMLResources.const.PROBLEM_RECORD_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           courseId = courseId,
                           problemSolvedMemberRecords = problemSolvedMemberRecords,
                           problemInformationRecords = problemInformationRecords,
                           chartSubmissionDescriptions = chartSubmissionDescriptions,
                           chartSubmissionRecords = chartSubmissionRecords)

@GradeServer.route('/problem/<problemId>/<courseId>')
@login_required
def user_record(problemId, courseId):
    
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
        problemSolvedUserRecords =dao.query(Submissions.memberId,
                                            Submissions.runTime,
                                            Submissions.sumOfSubmittedFileSize,
                                            Submissions.codeSubmissionDate,
                                            Submissions.usedMemory).\
                                      filter(Submissions.problemId == problemId,
                                             Submissions.courseId == courseId,
                                             Submissions.memberId == session[SessionResources.const.MEMBER_ID],
                                             Submissions.status == ENUMResources.const.SOLVED).\
                                      group_by(Submissions.memberId,
                                               Submissions.problemId,
                                               Submissions.courseId).\
                                      first()
    except Exception:
        problemSolvedUserRecords = []
        
    # Submitted Files
    try:
        count = dao.query(func.count(SubmittedFiles.fileIndex).label('count')).\
                    filter(SubmittedFiles.memberId == session[SessionResources.const.MEMBER_ID],
                           SubmittedFiles.problemId == problemId,
                           SubmittedFiles.courseId == courseId).\
                    first().\
                    count
    except Exception:
        count = 0
        
    # Submitted Files Information
    try:
        submittedFileRecords = dao.query(SubmittedFiles.fileName,
                                         SubmittedFiles.filePath).\
                                   filter(SubmittedFiles.memberId == session[SessionResources.const.MEMBER_ID],
                                          SubmittedFiles.problemId == problemId,
                                          SubmittedFiles.courseId == courseId).\
                                   all()
        fileData = []
        for raw in submittedFileRecords:
            # Open
            file = open(raw.filePath + raw.fileName)
            # Read
            data = file.read()
            # Close
            file.close()
            fileData.append(data)
    except Exception:
        submittedFileRecords = []
        fileData = []
   
    return render_template(HTMLResources.const.SUBMISSION_CODE_HTML,
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           submittedFileRecords = submittedFileRecords,
                           fileData = fileData,
                           problemName = problemName,
                           problemSolvedUserRecords = problemSolvedUserRecords)