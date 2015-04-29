
# -*- coding: utf-8 -*-

from sqlalchemy import func, and_

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.model.submissions import Submissions
from GradeServer.model.problems import Problems
from GradeServer.model.languages import Languages

'''
Submissions to Last Submitted
'''
def select_last_submissions(memberId = None, courseId = None, problemId = None):
    
    if courseId == OtherResources().const.ALL or (memberId and courseId and problemId):
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
                   filter((Submissions.courseId == courseId if courseId
                          else Submissions.courseId != None),
                          (Submissions.problemId == problemId if problemId
                           else Submissions.problemId != None),
                          (Submissions.memberId == memberId if memberId
                           else Submissions.memberId != None)).\
                   group_by(Submissions.memberId,
                            Submissions.problemId,
                            Submissions.courseId) 
'''
All Submission Record
'''
def select_all_submission(lastSubmission = None, memberId = None, courseId = None, problemId = None):
    try:
        if lastSubmission.name:
            return dao.query(Submissions.memberId,
                             Submissions.problemId,
                             Problems.problemName,
                             Submissions.courseId, 
                             Submissions.status,
                             Submissions.score,
                             Submissions.sumOfSubmittedFileSize,
                             Submissions.runTime,
                             Submissions.codeSubmissionDate,
                             Languages.languageName).\
                       join(lastSubmission,
                            and_(Submissions.solutionCheckCount == lastSubmission.c.solutionCheckCount,
                                 Submissions.memberId == lastSubmission.c.memberId,
                                 Submissions.courseId == lastSubmission.c.courseId,
                                 Submissions.problemId == lastSubmission.c.problemId)).\
                       join(Languages, 
                            Submissions.usedLanguageIndex == Languages.languageIndex).\
                       join(Problems,
                            Submissions.problemId == Problems.problemId)
    except Exception:
        return dao.query(Submissions.memberId,
                         Submissions.problemId,
                         Problems.problemName,
                         Submissions.courseId, 
                         Submissions.status,
                         Submissions.score,
                         Submissions.sumOfSubmittedFileSize,
                         Submissions.runTime,
                         Submissions.codeSubmissionDate,
                         Languages.languageName).\
                   filter((Submissions.memberId == memberId if memberId
                           else Submissions.memberId != None),
                          (Submissions.courseId == courseId if courseId
                           else Submissions.courseId != None),
                          (Submissions.problemId == problemId if problemId
                           else Submissions.problemId != None)).\
                   join(Languages, 
                        Submissions.usedLanguageIndex == Languages.languageIndex).\
                   join(Problems,
                        Submissions.problemId == Problems.problemId)
                                  
                                  
'''
Submissions Sorting Condition
'''
def submissions_sorted(submissions, sortCondition = OtherResources().const.SUBMISSION_DATE):
    
        # 제출날짜순 정렬
    if sortCondition == OtherResources().const.SUBMISSION_DATE:
        submissionRecords = dao.query(submissions).\
                                order_by(submissions.c.codeSubmissionDate.asc())
         # 실행 시간 순 정렬
    elif sortCondition == OtherResources().const.RUN_TIME:
        submissionRecords = dao.query(submissions).\
                                order_by(submissions.c.runTime.asc())
         # 코드 길이별 정렬         
    elif sortCondition == OtherResources().const.CODE_LENGTH:
        submissionRecords = dao.query(submissions).\
                                order_by(submissions.c.sumOfSubmittedFileSize.asc())  
                                 
    return submissionRecords