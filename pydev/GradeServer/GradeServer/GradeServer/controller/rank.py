# -*- coding: utf-8 -*-


from flask import render_template, request
from sqlalchemy import func

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilQuery import select_all_user, select_rank, rank_sorted, submissions_last_submitted, select_count
from GradeServer.utils.utilMessages import unknown_error, get_message

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

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
@GradeServer.route('/rank/<sortCondition>/page<pageNum>', methods = ['GET', 'POST'])
@login_required
def rank(sortCondition, pageNum, error =None):
    
    try:
        try:
            # Auto Complete MemberIds
            memberRecords = select_all_user().\
                            all()
        except Exception:
            memberRecords = []
            
        # Last Submission Max Count
        submissions = select_rank(submissions_last_submitted().subquery()).subquery()
        
        
        # records count
        try:
            count = select_count(submissions.c.memberId).first().\
                                                         count
        except Exception:
            count = 0
            
        # Paging Pointed
        pages = get_page_pointed(int(pageNum),
                                 count)
        
        # Find MemberId 뷰 호출
        if request.method == 'POST':
            # Finding MemberId
            findMemberId = request.form['memberId']
                        # 순차 탐색으로 찾아야 함
            for i in range(1, pages['allPage'] + 1):
                # memberId in Pages 
                rankSub = get_page_record(dao.query(submissions),
                                          i).subquery()
                # finding MemberId in Pages
                try:
                    if select_memberId(rankSub, findMemberId).first().\
                                                         memberId:
                        # Finding move to page
                        pageNum = i
                    
                        break
                except Exception:
                    pass
            else:
                        # 같은 아이디가 없을 때 메세지
                error = get_message('notExists')
       
                # 랭크 정보
        try:
            rankMemberRecords = get_page_record(rank_sorted(submissions,
                                                            sortCondition),
                                                int(pageNum)).all()
        except Exception:
            rankMemberRecords = []
            
        return render_template(HTMLResources.const.RANK_HTML,
                               SETResources = SETResources,
                               sortCondition =  sortCondition,
                               memberRecords = memberRecords,
                               rankMemberRecords = rankMemberRecords,
                               pages = pages,
                               error = error) # 페이지 정보
    except Exception:
        return unknown_error()     
    
    
'''
Select MemberId
'''
def select_memberId(rankSub, findMemberId):
    return dao.query(rankSub.c.memberId).\
               filter(rankSub.c.memberId == findMemberId)