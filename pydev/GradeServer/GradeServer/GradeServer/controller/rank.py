# -*- coding: utf-8 -*-


from flask import render_template, request
from sqlalchemy import func, distinct

from GradeServer.database import dao
from GradeServer.model.submissions import Submissions
from GradeServer.model.members import Members
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils import login_required, get_page_pointed, get_rank, unknown_error, get_message


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
@GradeServer.route('/rank/<sortCondition>?page<pageNum>', methods =["GET", "POST"])
@login_required
def rank(sortCondition, pageNum, error =None):
    
    try :
        #Rank members
        count =dao.query (func.count (distinct (Submissions.memberId)).label ("count")).first ().count
        try :
            # user Records
            memberRecords =dao.query (Members.memberId, Members.memberName).filter_by (authority ='User').all ()
        except Exception :
            memberRecords =[]
            
        submissions =dao.query (Submissions.memberId, Submissions.solutionCheckCount, Submissions.status).\
            group_by (Submissions.memberId, Submissions.problemId, Submissions.courseId).subquery ()
        
        # 랭크 정보
        rankMemberRecords =get_rank (submissions, sortCondition)
            
        # 일반적이 뷰 호출이 아닐 때
        if request.method == "POST" :
            LIST =15
            # 순차 탐색으로 찾아야 함
            for i in range (0, len (rankMemberRecords)) :
                if rankMemberRecords[i].memberId == request.form['memberId'] :
                    # 리스트 갯수만큼 
                    pageNum =i % LIST
                    
                    break
            else :
                # 같은 아이디가 없을 때 메세지
                error =get_message('notExists')
            
        return render_template('/rank.html', memberRecords =memberRecords, rankMemberRecords =rankMemberRecords,
                               pages =get_page_pointed (int(pageNum), count), error =error) # 페이지 정보
    except Exception :
        return unknown_error ()
        