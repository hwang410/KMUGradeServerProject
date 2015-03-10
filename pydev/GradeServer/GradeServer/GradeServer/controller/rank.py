# -*- coding: utf-8 -*-


from flask import render_template
from sqlalchemy import func, distinct

from GradeServer.database import dao
from GradeServer.model.submissions import Submissions
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils import login_required, get_page_pointed, get_rank


@GradeServer.teardown_request
def close_db_session(exception=None):
    """요청이 완료된 후에 db연결에 사용된 세션을 종료함"""
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))
        
"""
로그인한 유저가 랭크 페이지를 눌렀을 때
페이지 별로 보여줌
"""    
@GradeServer.route('/rank/page<pageNum>')
@login_required
def rank(pageNum):

    try :
        #Rank members
        count =dao.query (func.count (distinct (Submissions.memberId)).label ("count")).first ().count
        
        submissions =dao.query (Submissions.memberId, Submissions.solutionCheckCount, Submissions.status).\
            group_by (Submissions.memberId, Submissions.problemId, Submissions.courseId).subquery ()
        
        return render_template('/rank.html', rankMemberRecords =get_rank (submissions), pages =get_page_pointed (int(pageNum), count))
    
    except Exception :
        return render_template('/main.html', error ='Sorry Unknown Error!!!')