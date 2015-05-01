
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from sqlalchemy import func, and_

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.otherResources import OtherResources

from GradeServer.database import dao
from GradeServer.model.members import Members
from GradeServer.model.submissions import Submissions


'''
 DB Select basic rank
 '''
def select_rank(submissions):
    # # Total Submission Count (Rank Page Server Error Exception)
    submissionCount = dao.query(submissions.c.memberId,
                                func.sum(submissions.c.solutionCheckCount).label('solutionCheckCount')).\
                          group_by(submissions.c.memberId).\
                          subquery()
                          
        # 중복 제거푼 문제숫
    sumOfSolvedProblemCount = dao.query(Submissions.memberId).\
                                  join(submissions,
                                       and_(Submissions.status == ENUMResources().const.SOLVED,
                                            Submissions.memberId == submissions.c.memberId,
                                            Submissions.problemId == submissions.c.problemId,
                                            Submissions.courseId == submissions.c.courseId)).\
                                  group_by(Submissions.memberId,
                                           Submissions.problemId,
                                           Submissions.courseId).\
                                  subquery()
    sumOfSolvedProblemCount = dao.query(sumOfSolvedProblemCount,
                                        func.count(sumOfSolvedProblemCount.c.memberId).label('sumOfSolvedProblemCount')).\
                                        group_by(sumOfSolvedProblemCount.c.memberId).\
                                        subquery()
    
    #SubmitCount and SolvedCount Join
    return dao.query(submissionCount.c.memberId,
                     submissionCount.c.solutionCheckCount,
                     sumOfSolvedProblemCount.c.sumOfSolvedProblemCount,
                     (sumOfSolvedProblemCount.c.sumOfSolvedProblemCount / submissionCount.c.solutionCheckCount * 100).label('solvedRate')).\
               join(sumOfSolvedProblemCount,
                    submissionCount.c.memberId == sumOfSolvedProblemCount.c.memberId)


'''
Rank Sorting Condition
'''
def rank_sorted(ranks, sortCondition = OtherResources().const.RATE):
    #Get Comment
    # rate 정렬
    if sortCondition == OtherResources().const.RATE:
        rankMemberRecords = dao.query(ranks,
                                      Members.comment).\
                                join(Members,
                                     Members.memberId == ranks.c.memberId).\
                                order_by(ranks.c.solvedRate.asc())
    # Solved Problem Sorted
    elif sortCondition == OtherResources().const.SOLVED_PROBLEM:
        rankMemberRecords = dao.query(ranks,
                                      Members.comment).\
                                join(Members,
                                     Members.memberId == ranks.c.memberId).\
                                order_by(ranks.c.sumOfSolvedProblemCount.desc())
                                
    return rankMemberRecords

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