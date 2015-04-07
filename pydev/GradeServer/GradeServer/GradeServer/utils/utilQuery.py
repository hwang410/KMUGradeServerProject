# -*- coding: utf-8 -*-

from flask import session
from datetime import datetime, timedelta
from operator import attrgetter
from sqlalchemy import func

from GradeServer.utils.utils import *

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
               filter(Members.authority == USER)
    
    
'''
 DB Select Match MemberId
 '''
def select_match_member(memberId):
    # memberId Filterling
    return dao.query(Members).\
               filter(Members.memberId == memberId)


'''
허용된 과목 정보
'''
def select_accept_courses():
    # 서버 마스터는 모든 과목에 대해서, 그 외에는 지정된 과목에 대해서
    # Server Master
    if 'ServerAdministrator' in session['authority']:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse)
    # Class Master, User
    elif 'CourseAdministrator' in session['authority']:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse).\
                        filter(RegisteredCourses.courseAdministratorId == session['memberId'])
    else:
        myCourses = dao.query(Registrations.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse).\
                        filter(Registrations.memberId == session['memberId']).\
                        join(RegisteredCourses,
                             Registrations.courseId == RegisteredCourses.courseId)
            
    return myCourses

'''
 DB Select basic rank
 '''
def select_rank(submissions, sortCondition = RATE):
    #Get SubmitCount
    submissionCount = dao.query(submissions.c.memberId,
                                func.sum(submissions.c.solutionCheckCount).label('submissionCount')).\
                          group_by(submissions.c.memberId).\
                          subquery()
    #Get Solved Count
    status = dao.query(submissions.c.memberId,
                       func.count(submissions.c.status).label('solvedCount')).\
                 filter(submissions.c.status == SOLVED).\
                 group_by(submissions.c.memberId).subquery()
    #SubmitCount and SolvedCount Join
    submissions = dao.query(submissionCount.c.memberId,
                            submissionCount.c.submissionCount,
                            status.c.solvedCount,
                            (status.c.solvedCount / submissionCount.c.submissionCount * 100).label('solvedRate')).\
                      join(status,
                           submissionCount.c.memberId == status.c.memberId).\
                      subquery()
    #Get Comment
    # rate 정렬
    if sortCondition == RATE:
        rankMemberRecords = dao.query(submissions,
                                      Members.comment).\
                                join(Members,
                                     Members.memberId == submissions.c.memberId).\
                                order_by(submissions.c.solvedRate.desc())
    else: #if sortCondition == SOLVED_PROBLEM
        rankMemberRecords = dao.query(submissions,
                                      Members.comment).\
                                join(Members,
                                     Members.memberId == submissions.c.memberId).\
                                order_by(submissions.c.solvedCount.desc())
    
    return rankMemberRecords


'''
 DB Select Notices
 권한 별로 공지 가져오기
'''
def select_notices():
    # Notices Layer
    try:
        # 서버 공지만
        try:
            serverAdministratorId = dao.query(Members.memberId).\
                                        filter(Members.authority == SERVER_ADMINISTRATOR).\
                                        first().\
                                        memberId
            serverAdministratorNotices = dao.query(ArticlesOnBoard).\
                                             filter(ArticlesOnBoard.isNotice == NOTICE,
                                                    ArticlesOnBoard.writerId == serverAdministratorId).\
                                             subquery()
            serverAdministratorNotices = dao.query(serverAdministratorNotices,
                                                   RegisteredCourses.courseName).\
                                             join(RegisteredCourses,
                                                  serverAdministratorNotices.c.courseId == RegisteredCourses.courseId).\
                                             all()
        except Exception:
            serverAdministratorNotices = []
            
        # 로그인 상태
        try:
            from GradeServer.utils.loginRequired import login_required
            if login_required:
                # 서버 관리자는 모든 공지
                if SERVER_ADMINISTRATOR in session[AUTHORITY]:
                    notices = dao.query(ArticlesOnBoard,
                                        RegisteredCourses.courseName).\
                                  join(RegisteredCourses,
                                       ArticlesOnBoard.courseId == RegisteredCourses.courseId).\
                                  filter(ArticlesOnBoard.isNotice == NOTICE).\
                                  all()
                # 과목 관리자 및 유저는 담당 과목 공지
                else:
                    if COURSE_ADMINISTRATOR in session[AUTHORITY]:
                        registeredCourseId = dao.query(RegisteredCourses.courseId).\
                                                 filter(RegisteredCourses.courseAdministratorId == session[MEMBER_ID]).\
                                                 subquery()
                    # 학생인 경우
                    else: # elif User in session['authority']
                        registeredCourseId = dao.query(Registrations.courseId).\
                                                 filter(Registrations.memberId == session[MEMBER_ID]).\
                                                 subquery()
                    
                    # 해당 과목 추려내기
                    notices = dao.query(ArticlesOnBoard).\
                                  join(registeredCourseId,
                                       ArticlesOnBoard.courseId == registeredCourseId.c.courseId).\
                                  filter(ArticlesOnBoard.isNotice == NOTICE).\
                                  subquery()
                    # 과목이름 넣기
                    notices = dao.query(notices,
                                        RegisteredCourses.courseName).\
                                  join(RegisteredCourses,
                                       notices.c.courseId == RegisteredCourses.courseId).\
                                  all()
                    notices.extend(serverAdministratorNotices)
                    
        except Exception:
            # Not Login
            notices = serverAdministratorNotices

        # articleIndex 정렬
        notices = sorted(notices,
                         key = attrgetter('writtenDate'),
                         reverse = True)
        # 최대 5개만 보여주므로 그 밑에는 자르기
        if len(notices) > NOTICE_LIST:
            notices = notices[:NOTICE_LIST]   
    except Exception:
        # query get All Error None type Error
        notices = []
    
    return notices 

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