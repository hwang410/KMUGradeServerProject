
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
    
    if courseId == OtherResources().const.ALL or not(memberId or courseId or problemId):
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
                             Submissions.usedMemory,
                             Submissions.codeSubmissionDate,
                             Submissions.viewCount,
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
                         Submissions.usedMemory,
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


'''
Submissions Count
'''
def select_submission_count(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSubmissionCount'))

'''
Solved Problem Counts
'''
def select_solved_problem_count(submissions):
    submissions = dao.query(submissions).\
                      filter(submissions.c.status == ENUMResources().const.SOLVED).\
                      group_by(submissions.c.problemId,
                               submissions.c.courseId).\
                      subquery()
                      
    return dao.query(func.count(submissions.c.memberId).label('sumOfSolvedProblemCount'))

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
User Chart Information
'''
def select_member_chart_submission(submissions):
    return dao.query(select_solved_problem_count(submissions).subquery(),# 중복 제거푼 문제숫
                     select_submission_count(submissions).subquery(),# 총 제출 횟수
                     select_solved_count(submissions).subquery(),# 모든 맞춘 횟수
                     select_wrong_answer_count(submissions).subquery(),# 틀린 횟수
                     select_time_over_count(submissions).subquery(),# 타임 오버 횟수
                     select_compile_error_count(submissions).subquery(),# 컴파일 에러 횟수
                     select_runtime_error_count(submissions).subquery(),# 런타임 에러 횟수
                     select_server_error_count(submissions).subquery())# 서버 에러 횟수