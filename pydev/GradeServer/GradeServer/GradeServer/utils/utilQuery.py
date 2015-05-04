# -*- coding: utf-8 -*-

from flask import session
from datetime import datetime
from sqlalchemy import func


from GradeServer.resource.setResources import SETResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.model.members import Members
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.registrations import Registrations

        
        
'''
 DB Select All Members to User in Authority
 '''
def select_all_users():
        # 자동 완성을 위한 모든 유저기록
    print "In"
    return dao.query(Members.memberId,
                     Members.memberName).\
               filter(Members.authority == SETResources().const.USER)
    
'''
 DB Select MAtch Course
'''
def select_match_members_of_course(courseId):
    # courseId FilterLing
    members = select_all_users().subquery()
    return dao.query(Registrations.memberId,
                     members).\
               join(members,
                    Registrations.memberId == members.c.memberId)
                      
'''
 DB Select Match MemberId
 '''
def select_match_member(memberId):
    # memberId Filterling
    return dao.query(Members).\
               filter(Members.memberId == memberId)
def select_match_member_sub(members, memberId):
    # memberId Filterling
    return dao.query(members).\
               filter(members.c.memberId == memberId)
               

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
    if SETResources().const.SERVER_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse)
    # Class Master
    elif SETResources().const.COURSE_ADMINISTRATOR in session[SessionResources().const.AUTHORITY]:
        myCourses = dao.query(RegisteredCourses.courseId,
                              RegisteredCourses.courseName,
                              RegisteredCourses.endDateOfCourse).\
                        filter(RegisteredCourses.courseAdministratorId == session[SessionResources().const.MEMBER_ID])
    # User
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