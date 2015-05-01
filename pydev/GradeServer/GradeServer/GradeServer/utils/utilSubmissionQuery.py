
# -*- coding: utf-8 -*-

from sqlalchemy import func, and_

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.otherResources import OtherResources

from GradeServer.database import dao
from GradeServer.model.submittedFiles import SubmittedFiles
from GradeServer.model.submissions import Submissions
from GradeServer.model.problems import Problems
from GradeServer.model.submittedRecordsOfProblems import SubmittedRecordsOfProblems
from GradeServer.model.languages import Languages


'''
Submissions to Last Submitted
'''
def select_last_submissions(memberId = None, courseId = None, problemId = None):
    
    if courseId == OtherResources().const.ALL or not(memberId or courseId or problemId):
        return dao.query(Submissions.memberId,
                         Submissions.courseId,
                         Submissions.problemId,
                         func.max(Submissions.submissionCount).label('submissionCount'),
                         func.max(Submissions.solutionCheckCount).label('solutionCheckCount')).\
                   group_by(Submissions.memberId,
                            Submissions.problemId,
                            Submissions.courseId)
    else:   
        return dao.query(Submissions.memberId,
                         Submissions.courseId,
                         Submissions.problemId,
                         func.max(Submissions.submissionCount).label('submissionCount'),
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
def select_all_submissions(lastSubmission = None, memberId = None, courseId = None, problemId = None):
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
 Current Submissions
'''
def select_current_submissions(lastSubmission):
    return dao.query(Submissions.score,
                     Submissions.status,
                     lastSubmission).\
               join(lastSubmission,
                    and_(Submissions.memberId == lastSubmission.c.memberId,
                         Submissions.problemId == lastSubmission.c.problemId,
                         Submissions.courseId == lastSubmission.c.courseId,
                         Submissions.submissionCount == lastSubmission.c.submissionCount))
                      
                                                       
'''
Get SubmittedFiles
'''
def select_submitted_files(memberId, courseId, problemId):
    return dao.query(SubmittedFiles.fileName,
                     SubmittedFiles.filePath).\
               filter(SubmittedFiles.memberId == memberId,
                      SubmittedFiles.problemId == problemId,
                      SubmittedFiles.courseId == courseId)
                                       
                                       
                                                                         
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
Solved Submissions
'''
def select_solved_submissions(submissions):
    return dao.query(submissions).\
               filter(submissions.c.status == ENUMResources().const.SOLVED)



'''
Submissions Count
'''
def select_submissions_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSubmissionCount'))

'''
Solved Problem Counts
'''
def select_solved_problems_counts(submissions):
    submissions = dao.query(submissions).\
                      filter(submissions.c.status == ENUMResources().const.SOLVED).\
                      group_by(submissions.c.problemId,
                               submissions.c.courseId).\
                      subquery()
                      
    return dao.query(func.count(submissions.c.memberId).label('sumOfSolvedProblemCount'))

'''
Solved Counts
'''
def select_solved_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSolvedCount')).\
               filter(submissions.c.status == ENUMResources().const.SOLVED)
               
'''
Wrong Answer Counts
'''
def select_wrong_answer_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfWrongAnswerCount')).\
               filter(submissions.c.status == ENUMResources().const.WRONG_ANSWER)

'''
Time Over Counts
'''
def select_time_over_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfTimeOverCount')).\
               filter(submissions.c.status == ENUMResources().const.TIME_OVER)
               
'''
Compile Error Counts
'''
def select_compile_error_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfCompileErrorCount')).\
               filter(submissions.c.status == ENUMResources().const.COMPILE_ERROR)
               
'''
RunTime Error Counts
'''
def select_runtime_error_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfRunTimeErrorCount')).\
               filter(submissions.c.status == ENUMResources().const.RUNTIME_ERROR)

'''
Server Error Counts
'''
def select_server_error_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfServerErrorCount')).\
               filter(submissions.c.status == ENUMResources().const.SERVER_ERROR)
               
'''
Member Chart Information
'''
def select_member_chart_submissions(submissions):
    return dao.query(select_solved_problems_counts(submissions).subquery(),# 중복 제거푼 문제숫
                     select_submissions_counts(submissions).subquery(),# 총 제출 횟수
                     select_solved_counts(submissions).subquery(),# 모든 맞춘 횟수
                     select_wrong_answer_counts(submissions).subquery(),# 틀린 횟수
                     select_time_over_counts(submissions).subquery(),# 타임 오버 횟수
                     select_compile_error_counts(submissions).subquery(),# 컴파일 에러 횟수
                     select_runtime_error_counts(submissions).subquery(),# 런타임 에러 횟수
                     select_server_error_counts(submissions).subquery())# 서버 에러 횟수
    
    
    
'''
Problem Chart Information
'''
def select_problem_chart_submissions(sumOfSubmissionPeopleCount, sumOfSolvedPeopleCount, problemSubmittedRecords):
    return dao.query(sumOfSubmissionPeopleCount,
                     sumOfSolvedPeopleCount,
                     problemSubmittedRecords)
    
    
'''
Submitted Records Of problems
'''
def select_submitted_records_of_problem(courseId, problemId):
    return dao.query(SubmittedRecordsOfProblems.sumOfSubmissionCount, 
                     SubmittedRecordsOfProblems.sumOfSolvedCount, 
                     SubmittedRecordsOfProblems.sumOfWrongCount, 
                     SubmittedRecordsOfProblems.sumOfTimeOverCount, 
                     SubmittedRecordsOfProblems.sumOfCompileErrorCount, 
                     SubmittedRecordsOfProblems.sumOfRuntimeErrorCount ).\
               filter(SubmittedRecordsOfProblems.problemId == problemId,
                      SubmittedRecordsOfProblems.courseId == courseId)
               
               
'''
Sum Of Submitted People Counts
'''
def select_submissions_peoples_counts(submissions):
    return dao.query(func.count(submissions.c.memberId).label('sumOfSubmissionPeopleCount'))
      
'''
Sum Of Solved People Counts
'''
def select_solved_peoples_counts(submissions):
    
    return dao.query(func.count(submissions.c.memberId).label('sumOfSolvedPeopleCount')).\
               filter(submissions.c.status == ENUMResources().const.SOLVED)
