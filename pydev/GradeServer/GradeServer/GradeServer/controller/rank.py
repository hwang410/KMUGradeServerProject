# -*- coding: utf-8 -*-


from flask import render_template, request

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.checkInvalidAccess import check_invalid_access

from GradeServer.utils.memberCourseProblemParameter import MemberCourseProblemParameter

from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilQuery import select_all_users, select_count, select_match_member_sub, select_accept_courses
from GradeServer.utils.utilRankQuery import select_ranks, ranks_sorted
from GradeServer.utils.utilSubmissionQuery import select_last_submissions
from GradeServer.utils.utilMessages import unknown_error, get_message

from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.languageResources import LanguageResources

from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer


@GradeServer.teardown_request
def close_db_session(exception = None):
    """요청이 완료된 후에 db연결에 사용된 세션을 종료함"""
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))
        
"""
로그인한 유저가 랭크 페이지를 눌렀을 때
페이지 별로 보여줌
"""    
@GradeServer.route('/rank/<activeTabCourseId>-<sortCondition>/page<int:pageNum>', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def rank(activeTabCourseId, sortCondition, pageNum, error =None):
    
    try:
        findMemberId = None
        try:
            # Auto Complete MemberIds
            memberRecords = select_all_users().all()
        except Exception:
            memberRecords = []
            
        # Last Submission Max Count
        submissions = select_ranks(select_last_submissions(memberCourseProblemParameter = MemberCourseProblemParameter(memberId = None,
                                                                                                                       courseId = activeTabCourseId)).subquery()).subquery()
        
        # records count
        try:
            count = select_count(submissions.c.memberId).first().\
                                                         count
        except Exception:
            count = 0
            
        # Paging Pointed
        pages = get_page_pointed(pageNum = pageNum,
                                 count = count)
        submissions = ranks_sorted(submissions,
                                   sortCondition = sortCondition)
        # Find MemberId 뷰 호출
        if request.method == 'POST':
            # Finding MemberId
            findMemberId = request.form['memberId']
                        # 순차 탐색으로 찾아야 함
            for i in range(1, pages['allPage'] + 1):
                # memberId in Pages 
                ranks = get_page_record(submissions,
                                        pageNum = i).subquery()
                # finding MemberId in Pages
                try:
                    if select_match_member_sub(ranks,
                                               memberCourseProblemParameter = MemberCourseProblemParameter(memberId = findMemberId)).first().\
                                                                                                                                     memberId:
                        # Finding move to page
                        pageNum = i
                        # searchLine Check
                    
                        break
                except Exception:
                    pass
            else:
                                # 같은 아이디가 없을 때 메세지
                error = get_message('notExists')
       
                # 랭크 정보
        try:
            rankMemberRecords = get_page_record(submissions,
                                                pageNum = pageNum).all()
        except Exception:
            rankMemberRecords = []
        
        try:
            myCourses = select_accept_courses().all()
        except Exception:
            myCourses = []
        # myCourses Default Add ALL
        myCourses.insert(0, OtherResources().const.ALL)
       
        return render_template(HTMLResources().const.RANK_HTML,
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               activeTabCourseId = activeTabCourseId,
                               sortCondition =  sortCondition,
                               memberRecords = memberRecords,
                               rankMemberRecords = rankMemberRecords,
                               myCourses = myCourses,
                               pages = pages,
                               findMemberId = findMemberId,
                               error = error) # 페이지 정보
    except Exception:
        return unknown_error()     