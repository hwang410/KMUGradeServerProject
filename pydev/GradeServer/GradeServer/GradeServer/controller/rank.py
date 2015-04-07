# -*- coding: utf-8 -*-


from flask import render_template, request
from sqlalchemy import func

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilQuery import select_all_user, select_rank
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.utils import *

from GradeServer.database import dao
from GradeServer.model.submissions import Submissions
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
            memberRecords = dao.query(select_all_user().subquery()).\
                                all()
        except Exception:
            memberRecords = []
            
        submissions = select_rank(dao.query(Submissions.memberId,
                                            Submissions.solutionCheckCount,
                                            Submissions.status).\
                                      group_by(Submissions.memberId,
                                               Submissions.problemId,
                                               Submissions.courseId).subquery(),
                                  sortCondition)
        
        
        # records count
        try:
            count = dao.query(func.count(submissions.c.memberId).label('count')).\
                        first().\
                        count
        except Exception:
            count = 0
            
        # Paging Pointed
        pages = get_page_pointed(int(pageNum),
                                count)
        
        # Find MemberId 뷰 호출
        if request.method == 'POST':
                        # 순차 탐색으로 찾아야 함
            for i in range(pages['allPage'] + 1):
                rankSub = get_page_record(submissions,
                                          i).\
                                  subquery()
                # finding MemberId in Pages
                try:
                    if dao.query(rankSub.c.memberId).\
                        filter(rankSub.c.memberId == request.form['memberId']).\
                        first().\
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
            rankMemberRecords = get_page_record(submissions,
                                                int(pageNum)).\
                                all()
        except Exception:
            rankMemberRecords = []
            
        return render_template(RANK_HTML,
                               sortCondition =  sortCondition,
                               memberRecords = memberRecords,
                               rankMemberRecords = rankMemberRecords,
                               pages = pages,
                               error = error) # 페이지 정보
    except Exception:
        return unknown_error()        