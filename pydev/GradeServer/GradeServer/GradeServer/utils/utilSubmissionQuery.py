
# -*- coding: utf-8 -*-

from sqlalchemy import func

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.model.submissions import Submissions


'''
Submissions to Last Submitted
'''
def submissions_last_submitted(courseId):
    
    if courseId == OtherResources.const.ALL or not courseId:
        return dao.query(Submissions.memberId,
                         Submissions.courseId,
                         Submissions.problemId,
                         func.max(Submissions.solutionCheckCount).label('solutionCheckCount')).\
                   group_by(Submissions.memberId,
                            Submissions.problemId,
                            Submissions.courseId)
    else:    
        return dao.query(Submissions.memberId,
                         Submissions.courseId,
                         Submissions.problemId,
                         func.max(Submissions.solutionCheckCount).label('solutionCheckCount')).\
                   filter(Submissions.courseId == courseId).\
                   group_by(Submissions.memberId,
                            Submissions.problemId,
                            Submissions.courseId) 
'''
All Submission Record
'''
def select_all_submission(memberId, problemId, courseId):
    return dao.query(Submissions.memberId,
                                Submissions.problemId,
                                Submissions.courseId, 
                                Submissions.status,
                                Submissions.score,
                                Submissions.sumOfSubmittedFileSize,
                                Submissions.runTime,
                                Submissions.usedLanguage,
                                Submissions.codeSubmissionDate,
                                Languages.languageName).\
                          filter(Submissions.memberId == memberId).\
                          join(Languages, 
                                Submissions.usedLanguage == Languages.languageIndex).\
                                  
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