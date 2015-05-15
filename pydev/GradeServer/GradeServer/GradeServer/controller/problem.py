# -*- coding: utf-8 -*-

from flask import request, session, render_template, url_for, redirect, flash

from datetime import datetime

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.checkInvalidAccess import check_invalid_access

from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilQuery import select_count
from GradeServer.utils.utilSubmissionQuery import submissions_sorted, select_last_submissions, select_all_submissions, select_current_submissions,\
                                                  select_submissions_peoples_counts, select_solved_peoples_counts, select_submitted_records_of_problem,\
                                                  select_problem_chart_submissions, select_solved_submissions, select_submitted_files
from GradeServer.utils.utilProblemQuery import join_problems_names, select_problems_of_course, join_problem_lists_submissions, select_problem_informations,\
                                               update_submission_code_view_count
                                               
from GradeServer.utils.utilMessages import unknown_error, get_message

from GradeServer.utils.memberCourseProblemParameter import MemberCourseProblemParameter

from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer

from GradeServer.model.registeredCourses import RegisteredCourses
from itertools import count


@GradeServer.route('/problem_list/<courseId>/page<pageNum>')
@check_invalid_access
@login_required
def problem_list(courseId, pageNum):
    """ problem submitting page """
    try:
        # Get Last Submitted History
        lastSubmission = select_last_submissions(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = session[SessionResources().const.MEMBER_ID],
                                                                                                             courseId = courseId)).subquery()
        # Current Submission                                      
        submissions = select_current_submissions(lastSubmission).subquery()
        
        # Get Problem Informations
        problems = join_problems_names(select_problems_of_course(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                             courseId = courseId)).subquery()).subquery()
        # Get ProblemList Count
        try:
            count = select_count(problems.c.problemId).first().\
                                                       count
        except Exception:
            count = 0
        # Get ProblemListRecords OuterJoin
        try:
            problemListRecords = get_page_record(join_problem_lists_submissions(problems,
                                                                                submissions),
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
    except Exception:
        return unknown_error()


@GradeServer.route('/problem/<courseId>/<problemId>?page<pageNum>')
@check_invalid_access
@login_required
def problem(courseId, problemId, pageNum):
    """
    use db to get its problem page
    now, it moves to just default problem page
    """
    try :
        # Get startDateOfSubmission of Problem
        try:
            startDateOfSubmission = select_problems_of_course(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                          courseId = courseId,
                                                                                                                          problemId = problemId)).first().\
                                                              startDateOfSubmission
        except Exception:
            startDateOfSubmission = None
            
        # are Not Access. conditions is an Administrator and endOfSubmission ago
        if SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]\
           or SETResources().const.COURSE_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]\
           or startDateOfSubmission <= datetime.now():
            
            try:
                from GradeServer.utils.utilCodeSubmissionQuery import select_languages
                languageInfoRecords = select_languages(courseId = courseId).all()
            except Exception:
                languageInfoRecords = []
    
            try:
                problemInformation = select_problem_informations(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                             courseId = courseId,
                                                                                                                             problemId = problemId)).first()
            except Exception:
                problemInformation = []    
    
            browserName = request.user_agent.browser
            browserVersion = request.user_agent.version
            print browserName, browserVersion
            return render_template(HTMLResources().const.PROBLEM_HTML,
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
                                   courseId = courseId,
                                   problemId = problemId,
                                   problemInformation = problemInformation,
                                   problemName = problemInformation.problemName.replace(' ', ''),
                                   languageInfoRecords = languageInfoRecords,
                                   pageNum = pageNum,
                                   browserName = browserName,
                                   browserVersion = browserVersion)
    
        # Access Rejection
        else:
            flash('제출 기간이 아닙니다!!!')
            return redirect(url_for(RouteResources().const.PROBLEM_LIST,
                                    courseId = courseId,
                                    pageNum = pageNum))
    except Exception:
        return unknown_error()
    
    

"""
    in the main page, it uses methods so 
    before login, need to block to access to other menus
"""
        
@GradeServer.route('/problem', methods=['GET', 'POST'])
@check_invalid_access
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

@GradeServer.route('/problem_record/<courseId>-<problemId>/<sortCondition>')
@check_invalid_access
@login_required
def problem_record(courseId, problemId, sortCondition = OtherResources().const.RUN_TIME):
    """
    navbar - class - Record of problem
    """
    try:
        # Chart View Value Text
        chartSubmissionDescriptions = ['Tried People',
                                       'Solved People',
                                       'Submission Count',
                                       'Solved',
                                       'Wrong Answer',
                                       'Time Over',
                                       'Compile Error',
                                       'Runtime Error']
        
        # last Submissions Info
        submissions = select_all_submissions(lastSubmission = select_last_submissions(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                                                  courseId = courseId,
                                                                                                                                                  problemId = problemId)).subquery(),
                                            memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                        courseId = courseId,
                                                                                                        problemId = problemId)).subquery()
        try:
            # Submitted Members Count
            sumOfSubmissionPeopleCount = select_submissions_peoples_counts(submissions).subquery()
            # Solved Members Count
            sumOfSolvedPeopleCount = select_solved_peoples_counts(submissions).subquery()
            # Problem Rrecord
            problemSubmittedRecords = select_submitted_records_of_problem(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                                      courseId = courseId,
                                                                                                                                      problemId = problemId)).subquery()
            # Chart SubmissionRecords
            chartSubmissionRecords = select_problem_chart_submissions(sumOfSubmissionPeopleCount,
                                                                      sumOfSolvedPeopleCount,
                                                                      problemSubmittedRecords).first()
        except:
            print 'SubmittedRecordsOfProblems table is empty'
            chartSubmissionRecords = []
            
        # Problem Information (LimitedTime, LimitedMemory
        try:
            problemInformationRecords = select_problem_informations(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                                courseId = None,
                                                                                                                                problemId = problemId)).first()
        except Exception:
            problemInformationRecords = []
        # Problem Solved Users
        try:
            # Problem Solved Member
            problemSolvedMemberRecords = submissions_sorted(select_solved_submissions(submissions).subquery(),
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
    except Exception:
        return unknown_error()
    
    

@GradeServer.route('/submission_code/<memberId>/<courseId>-<problemId>')
@check_invalid_access
@login_required
def submission_code(memberId, courseId, problemId, error = None):
    
    try:
        # Get endDateOfSubmission of Problem
        try:
            endDateOfSubmission = select_problems_of_course(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                        courseId = courseId,
                                                                                                                        problemId = problemId)).first().\
                                                            endDateOfSubmission
        except Exception:
            endDateOfSubmission = None
            
        # are Not Access. conditions is an Administrator and endOfSubmission ago
        if SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]\
           or SETResources().const.COURSE_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]\
           or endDateOfSubmission <= datetime.now():
            
            # last Submissions Info
            lastSubmission = select_last_submissions(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = memberId,
                                                                                                                 courseId = courseId,
                                                                                                                 problemId = problemId)).subquery()
            # Code View Count Up
            update_submission_code_view_count(lastSubmission,
                                              memberCourseProblemParameter = MemberCourseProblemParameter(memberId = memberId,
                                                                                                          courseId = courseId,
                                                                                                          problemId = problemId))
            # Commit Exception
            try:
                dao.commit()
            except Exception:
                dao.rollback()
                error = get_message('updateFailed')
                
            # Problem Information (LimitedTime, LimitedMemory
            try:
                problemName = select_problem_informations(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                      courseId = None,
                                                                                                                      problemId = problemId)).first().\
                                                                     problemName
            except Exception:
                problemName = None
                
            # Problem Solved Users
            try:
                # last Submissions Info
                submissions = select_all_submissions(lastSubmission,
                                                     memberCourseProblemParameter = MemberCourseProblemParameter(memberId = memberId,
                                                                                                                 courseId = courseId,
                                                                                                                 problemId = problemId)).subquery()
                problemSolvedMemberRecords = select_solved_submissions(submissions).first()
            except Exception:
                problemSolvedMemberRecords = []
                
            # Submitted Files Information
            try:
                submittedFileRecords = select_submitted_files(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = memberId, 
                                                                                                                          courseId = courseId,
                                                                                                                          problemId = problemId)).all()
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
                                   problemSolvedMemberRecords = problemSolvedMemberRecords,
                                   error = error)
        #Access Rejection
        else:
            flash('코드를 볼 권한이 없습니다!!!')
            return redirect(url_for(RouteResources().const.PROBLEM_RECORD,
                                    courseId = courseId,
                                    problemId = problemId,
                                    sortCondition = OtherResources().const.RUN_TIME))
    except Exception:
        return unknown_error()
