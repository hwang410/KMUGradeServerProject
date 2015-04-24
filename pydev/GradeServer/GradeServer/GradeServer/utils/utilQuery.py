# -*- coding: utf-8 -*-

from flask import session
from datetime import datetime, timedelta
from sqlalchemy import func

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.model.members import Members
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.registrations import Registrations
from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.submissions import Submissions

'''
 DB Select All Members to User in Authority
 '''
def select_all_user():
        # 자동 완성을 위한 모든 유저기록
    return dao.query(Members.memberId,
                     Members.memberName).\
               filter(Members.authority == SETResources.const.USER)
    
    
'''
 DB Select Match MemberId
 '''
def select_match_member(memberId):
    # memberId Filterling
    return dao.query(Members).\
               filter(Members.memberId == memberId)


'''
Record count
'''
def select_count(keySub):
    return dao.query(func.count(keySub).label('count'))



'''
허용된 과목 정보
'''
def select_accept_courses():
    # 서버 마스터는 모든 과목에 대해서, 그 외에는 지정된 과목에 대해서
    # Server Master
    if SETResources.const.SERVER_ADMINISTRATOR in session[SessionResources.const.AUTHORITY]:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse)
    # Class Master, User
    elif SETResources.const.COURSE_ADMINISTRATOR in session['SessionResources.const.AUTHORITY']:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse).\
                        filter(RegisteredCourses.courseAdministratorId == session[SessionResources.const.MEMBER_ID])
    else:
        myCourses = dao.query(Registrations.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse).\
                        filter(Registrations.memberId == session[SessionResources.const.MEMBER_ID]).\
                        join(RegisteredCourses,
                             Registrations.courseId == RegisteredCourses.courseId)
            
    return myCourses

'''
Submissions to Last Submitted
'''
def submissions_last_submitted():
    
    return dao.query(Submissions.memberId,
                     Submissions.courseId,
                     Submissions.problemId,
                     func.max(Submissions.solutionCheckCount).label('solutionCheckCount')).\
               group_by(Submissions.memberId,
                        Submissions.problemId,
                        Submissions.courseId)
                                                   
           
''' 
Submissions Duplication Solved Exception
'''
def sum_of_solved_problem_count(submissions):
    
    return dao.query(submissions.c.memberId,
                     func.count(submissions.c.memberId).label('sumOfSolvedProblemCount')).\
               filter(submissions.c.status == ENUMResources.const.SOLVED)
                            
                            
                                          
'''
 DB Select basic rank
 '''
def select_rank(submissions):
    # # Total Submission Count (Rank Page Server Error Exception)
    submissionCount = dao.query(submissions.c.memberId,
                                func.sum(submissions.c.solutionCheckCount).label('sumOfSubmissionCounts')).\
                          group_by(submissions.c.memberId).\
                          subquery()
        # 중복 제거푼 문제숫
    sumOfSolvedProblemCount = sum_of_solved_problem_count(dao.query(Submissions.problemId,
                                                                    Submissions.courseId,
                                                                    Submissions.status,
                                                                    submissionCount).\
                                                              filter(Submissions.status == ENUMResources.const.SOLVED).\
                                                              join(submissionCount,
                                                                   Submissions.memberId == submissionCount.c.memberId).\
                                                              group_by(Submissions.memberId,
                                                                       Submissions.problemId,
                                                                       Submissions.courseId).\
                                                              subquery()).\
                                  subquery()
    #SubmitCount and SolvedCount Join
    submissions = dao.query(submissionCount.c.memberId,
                            submissionCount.c.sumOfSubmissionCounts,
                            sumOfSolvedProblemCount.c.sumOfSolvedProblemCount,
                            (sumOfSolvedProblemCount.c.sumOfSolvedProblemCount / submissionCount.c.sumOfSubmissionCounts * 100).label('solvedRate')).\
                      join(sumOfSolvedProblemCount,
                           submissionCount.c.memberId == sumOfSolvedProblemCount.c.memberId)
    
    return submissions


'''
Rank Sorting Condition
'''
def rank_sorted(ranks, sortCondition = OtherResources.const.RATE):
    #Get Comment
    # rate 정렬
    if sortCondition == OtherResources.const.RATE:
        rankMemberRecords = dao.query(ranks,
                                      Members.comment).\
                                join(Members,
                                     Members.memberId == ranks.c.memberId).\
                                order_by(ranks.c.solvedRate.asc())
    # Solved Problem Sorted
    elif sortCondition == OtherResources.const.SOLVED_PROBLEM:
        rankMemberRecords = dao.query(ranks,
                                      Members.comment).\
                                join(Members,
                                     Members.memberId == ranks.c.memberId).\
                                order_by(ranks.c.sumOfSolvedProblemCount.desc())
                                
    return rankMemberRecords

                            
                            
'''
Submissions Sorting Condition
'''
def submissions_sorted(submissions, sortCondition = OtherResources.const.SUBMISSION_DATE):
    
    print "CCCCCC", sortCondition
        # 제출날짜순 정렬
    if sortCondition == OtherResources.const.SUBMISSION_DATE:
        print "DDDDD"
        submissionRecords = dao.query(submissions).\
                                order_by(submissions.c.codeSubmissionDate.desc())
        print "EEEEE"
         # 실행 시간 순 정렬
    elif sortCondition == OtherResources.const.RUN_TIME:
        submissionRecords = dao.query(submissions).\
                                order_by(submissions.c.runTime.asc())
         # 코드 길이별 정렬         
    elif sortCondition == OtherResources.const.CODE_LENGTH:
        submissionRecords = dao.query(submissions).\
                                order_by(submissions.c.sumOfSubmittedFileSize.asc())  
                                 
    return submissionRecords


'''
 DB Select Notices
 권한 별로 공지 가져오기
'''
def select_notices():
    # Notices Layer
    try:
        # 서버 공지만
        try:
            try:
                serverAdministratorId = dao.query(Members.memberId).\
                                            filter(Members.authority == SETResources.const.SERVER_ADMINISTRATOR).\
                                            first().\
                                            memberId
            except:
                serverAdministratorId = None
                
            publicNoticeRecords = select_simple_notice().filter(ArticlesOnBoard.writerId == serverAdministratorId).\
                                                         all()
        except Exception:
            publicNoticeRecords = []
            
        # 로그인 상태
        try:
            from GradeServer.utils.loginRequired import login_required
            if login_required:
                # 서버 관리자는 모든 공지
                if SETResources.const.SERVER_ADMINISTRATOR in session[SessionResources.const.AUTHORITY]:
                    noticeRecords = select_simple_notice().all()
                # 과목 관리자 및 유저는 담당 과목 공지
                else:
                    if SETResources.const.COURSE_ADMINISTRATOR in session[SessionResources.const.AUTHORITY]:
                        registeredCourseId = dao.query(RegisteredCourses.courseId).\
                                                 filter(RegisteredCourses.courseAdministratorId == session[SessionResources.const.MEMBER_ID]).\
                                                 subquery()
                    # 학생인 경우
                    else: # elif User in session['authority']
                        registeredCourseId = dao.query(Registrations.courseId).\
                                                 filter(Registrations.memberId == session[SessionResources.const.MEMBER_ID]).\
                                                 subquery()
                    
                    # 해당 과목 추려내기
        # slicke 0 ~ NOTICE_LIST
                    noticeRecords = dao.query(ArticlesOnBoard.articleIndex,
                                              ArticlesOnBoard.courseId,
                                              ArticlesOnBoard.title,
                                              ArticlesOnBoard.replyCount,
                                              ArticlesOnBoard.content,
                                              ArticlesOnBoard.writtenDate,
                                              RegisteredCourses.courseName).\
                                        join(registeredCourseId,
                                             ArticlesOnBoard.courseId == registeredCourseId.c.courseId).\
                                        join(RegisteredCourses,
                                             ArticlesOnBoard.courseId == RegisteredCourses.courseId).\
                                        filter(ArticlesOnBoard.isNotice == ENUMResources.const.TRUE).\
                                        order_by(ArticlesOnBoard.writtenDate.desc()).\
                                        slice(0, OtherResources.const.NOTICE_LIST).\
                                        all()
        except Exception:
            # Not Login
            noticeRecords = publicNoticeRecords
    except Exception:
        # query get All Error None type Error
        noticeRecords = []
    
    return noticeRecords 


''' 
Get Notices
'''
def select_simple_notice():
    
    return dao.query(ArticlesOnBoard.articleIndex,
                     ArticlesOnBoard.courseId,
                     ArticlesOnBoard.title,
                     ArticlesOnBoard.replyCount,
                     ArticlesOnBoard.content,
                     ArticlesOnBoard.writtenDate,
                     RegisteredCourses.courseName).\
               join(RegisteredCourses,
                    ArticlesOnBoard.courseId == RegisteredCourses.courseId).\
               filter(ArticlesOnBoard.isNotice == ENUMResources.const.TRUE)

                                                    
'''
Top Coder
'''
def select_top_coder():
    # Top Coder Layer
    try:
        # 오늘 요일 월1 ~ 일7
        dayOfWeekNum = datetime.now().isoweekday()
        # 요일 별 제출 기간 추려내기
        minusDays = {1: -1,
                                         2: -2,
                                         3: -3,
                                         4: -4,
                                         5: -5,
                                         6: -6,
                                         7: -0}
        addDays = {1: 5,
                                    2: 4,
                                    3: 3,
                                    4: 2,
                                    5: 1,
                                    6: 0,
                                    7: 6}
        # 금주의 시작일과 끝일 구함
        submissionDatePeriod = dayOfWeek(minusDays = minusDays[dayOfWeekNum],
                                         addDays = addDays[dayOfWeekNum])
        # 이번주에 낸 제출 목록 
        dayOfWeekSubmissions = dao.query(Submissions.memberId,
                                         Submissions.solutionCheckCount,
                                         Submissions.status).\
                                    filter(Submissions.codeSubmissionDate.between(submissionDatePeriod['start'],
                                                                                  submissionDatePeriod['end'])).\
                                    group_by(Submissions.memberId,
                                             Submissions.problemId,
                                             Submissions.courseId).\
                                    subquery()

        try:
            # return subquery
            topCoder = dao.query(select_rank(dayOfWeekSubmissions)).\
                           first()
            topCoderId = topCoder[0].memberId
        except Exception:
            topCoderId = None
    except Exception:
        # None Type Error
        from GradeServer.utils.utilMessages import get_message
        topCoderId = get_message('unknown')
        
    return topCoderId


# 요일 별로 금주 기간 지정
def dayOfWeek(minusDays, addDays, dateFormat = '%Y-%m-%d'):
    # 현재 날짜에서 addDays일후 날짜까지 구함
    startDate = (datetime.now() + timedelta(days = minusDays)).strftime(dateFormat)
    endDate = (datetime.now() + timedelta(days = addDays)).strftime(dateFormat) 
    submissionDatePeriod = {'start': startDate,
                            'end': endDate}
    
    return submissionDatePeriod