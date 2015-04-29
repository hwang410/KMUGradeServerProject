# -*- coding: utf-8 -*-

from flask import session
from datetime import datetime
from sqlalchemy import func, or_

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.utils.utilPaging import get_page_record

from GradeServer.database import dao
from GradeServer.model.members import Members
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.registrations import Registrations
from GradeServer.model.articlesOnBoard import ArticlesOnBoard

'''
 DB Select All Members to User in Authority
 '''
def select_all_user():
        # 자동 완성을 위한 모든 유저기록
    return dao.query(Members.memberId,
                     Members.memberName).\
               filter(Members.authority == SETResources().const.USER)
    
    
'''
 DB Select Match MemberId
 '''
def select_match_member(memberId):
    # memberId Filterling
    return dao.query(Members).\
               filter(Members.memberId == memberId)
def select_match_member_sub(memberSub, memberId):
    # memberId Filterling
    return dao.query(memberSub).\
               filter(Members.memberId == memberId)
               

'''
Record count
'''
def select_count(keySub):
    return dao.query(func.count(keySub).label('count'))

'''
Sum Of Submitted People Counts
'''
def select_submission_people_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSubmissionPeopleCount')).\
               group_by(submissions.c.memberId,
                        submissions.c.problemId,
                        submissions.c.courseId)
               
'''
Sum Of Solved People Counts
'''
def select_solved_people_count(submissions):
    return dao.query(func.count(submissions.c.memberId.distinct()).label('sumOfSolvedPeopleCount')).\
               filter(submissions.c.status == ENUMResources().const.SOLVED).\
               group_by(submissions.c.memberId,
                        submissions.c.problemId,
                        submissions.c.courseId,
                        submissions.c.status)

'''
Submissions Count
'''
def select_submission_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSubmissionCount'))

'''
Solved Problem Counts
'''
def select_solved_problem_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSolvedProblemCount')).\
               filter(submissions.c.status == ENUMResources().const.SOLVED).\
               group_by(submissions.c.problemId,
                        submissions.c.courseId)

'''
Solved Counts
'''
def select_solved_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSolvedCount')).\
               filter(submissions.c.status == ENUMResources().const.SOLVED)
               
'''
Wrong Answer Counts
'''
def select_wrong_answer_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfWrongAnswerCount')).\
               filter(submissions.c.status == ENUMResources().const.WRONG_ANSWER)

'''
Time Over Counts
'''
def select_time_over_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfTimeOverCount')).\
               filter(submissions.c.status == ENUMResources().const.TIME_OVER)
               
'''
Compile Error Counts
'''
def select_compile_error_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfCompileErrorCount')).\
               filter(submissions.c.status == ENUMResources().const.COMPILE_ERROR)
               
'''
RunTime Error Counts
'''
def select_runtime_error_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfRunTimeErrorCount')).\
               filter(submissions.c.status == ENUMResources().const.RUNTIME_ERROR)

'''
Server Error Counts
'''
def select_server_error_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfServerErrorCount')).\
               filter(submissions.c.status == ENUMResources().const.SERVER_ERROR)
               

'''
허용된 과목 정보
'''
def select_accept_courses():
    # 서버 마스터는 모든 과목에 대해서, 그 외에는 지정된 과목에 대해서
    # Server Master
    if SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse)
    # Class Master, User
    elif SETResources().const.COURSE_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse).\
                        filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID])
    else:
        myCourses = dao.query(Registrations.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse).\
                        filter(Registrations.memberId == session[SessionResources().const.MEMBER_ID]).\
                        join(RegisteredCourses,
                             Registrations.courseId == RegisteredCourses.courseId)
            
    return myCourses


'''
Select Past, Current course
'''
def select_past_courses(myCourses):
    return dao.query(myCourses).\
               filter(myCourses.c.endDateOfCourse < datetime.now())
def select_current_courses(myCourses):
    return dao.query(myCourses).\
               filter(myCourses.c.endDateOfCourse >= datetime.now())
               
           
'''
 DB Select Notices
 권한 별로 공지 가져오기
'''
def select_notices():
    # Notices Layer
    from GradeServer.utils.loginRequired import login_required
            # 로그인 상태
    if session:
        try:
                         # 서버 관리자는 모든 공지
            if SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]:
                noticeRecords = select_simple_notice(dao.query(ArticlesOnBoard).\
                                                         subquery()).all()
                       # 과목 관리자 및 유저는 담당 과목 공지
            else:
                # Course Administrator
                if SETResources().const.COURSE_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]:
                    registeredCoursesId = dao.query(RegisteredCourses.courseId).\
                                             filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID]).\
                                             subquery()
                                 # 학생인 경우
                else: # elif User in session['authority']
                    registeredCoursesId = dao.query(Registrations.courseId).\
                                             filter(Registrations.memberId == session[SessionResources().const.MEMBER_ID]).\
                                             subquery()
                
                                # 해당 과목 추려내기
                # slice 0 ~ NOTICE_LIST
                noticeRecords = select_simple_notice(dao.query(ArticlesOnBoard).\
                                                         join(registeredCoursesId,
                                                              or_(ArticlesOnBoard.courseId == registeredCoursesId.c.courseId,
                                                                  ArticlesOnBoard.courseId == None)).\
                                                         subquery()).subquery()
                noticeRecords = get_page_record(dao.query(noticeRecords).\
                                                    order_by(noticeRecords.c.writtenDate.desc()),
                                                    
                                                int(1),
                                                OtherResources().const.NOTICE_LIST).all()   
        except Exception:
            noticeRecords = []
    # Not Login     
    else:  
                # 서버 공지만
        try:
            try:
                serverAdministratorId = dao.query(Members.memberId).\
                                            filter(Members.authority == SETResources().const.SERVER_ADMINISTRATOR).\
                                            first().\
                                            memberId
            except:
                serverAdministratorId = None
            # Get Server Notice
            noticeRecords = select_simple_notice(select_server_notice(serverAdministratorId).subquery()).all()
        except Exception:
            # query get All Error None type Error
            noticeRecords = []

    return noticeRecords 


''' 
Ger SErverNotices
'''
def select_server_notice(serverAdministratorId):
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.writerId == serverAdministratorId,
                      ArticlesOnBoard.isNotice == ENUMResources().const.TRUE)
               
               
''' 
Get Notices
'''
def select_simple_notice(articlesSub):
    
    return dao.query(articlesSub,
                     RegisteredCourses.courseName).\
               join(RegisteredCourses,
                    or_(articlesSub.c.courseId == RegisteredCourses.courseId,
                        articlesSub.c.courseId == None)).\
               filter(articlesSub.c.isNotice == ENUMResources().const.TRUE)

                                                    
