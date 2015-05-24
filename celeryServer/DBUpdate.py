import sys
from DBManager import db_session
from DB.submissions import Submissions
from DB.submittedRecordsOfProblems import SubmittedRecordsOfProblems

STATUS = ['grading status', 'NeverSubmitted', 'Judging', 'Solved', 'TimeOver',
          'WrongAnswer', 'CompileError', 'RunTimeError', 'ServerError']

class DBUpdate(object):
    def __init__(self, stdNum, problemNum, courseNum, submitCount):
        self.stdNum = stdNum
        self.problemNum = problemNum
        self.courseNum = courseNum
        self.submitCount = submitCount
        
    def ResutlUpdate(self, messageParaList):
        try:
            if len(messageParaList) != 4:
                self.UpdateServerError()
        
            result = messageParaList[0]
            score = messageParaList[1]
            runTime = messageParaList[2]
            usingMem = messageParaList[3]
            
            if result == 'WrongAnswer':
                self.SubmittedRecordsOfProblems_WrongAnswer(result, score, runTime, usingMem)
            
            elif result == 'TimeOver':
                self.SubmittedRecordsOfProblems_TimbeOver(result, score, runTime, usingMem)
            
            elif result == 'Solved':
                self.SubmittedRecordsOfProblems_Solved(result, score, runTime, usingMem)
                
            elif result == 'RunTimeError':
                self.SubmittedRecordsOfProblems_RunTimeError(result, score, runTime, usingMem)
                
            elif result == 'CompileError':
                self.SubmittedRecordsOfProblems_CompileError(result, score, runTime, usingMem)
                
            else:
                self.UpdateServerError()
                
            if result == 'ServerError':
                self.UpdateServerError()
                
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise e
        
    def SubmittedRecordsOfProblems_CompileError(self, result, score, runTime, usingMem):
        try:
            db_session.query(Submissions).\
                filter_by(memberId = self.stdNum,
                          problemId = self.problemNum,
                          courseId = self.courseNum,
                          submissionCount = self.submitCount).\
                update(dict(status = STATUS.index(result),
                            score = score,
                            runTime = runTime,
                            usedMemory = usingMem,
                            solutionCheckCount = Submissions.solutionCheckCount+1))
                
            db_session.query(SubmittedRecordsOfProblems).\
                filter_by(problemId = self.problemNum,
                          courseId = self.courseNum).\
                          update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                      sumOfCompileErrorCount = SubmittedRecordsOfProblems.sumOfCompileErrorCount + 1))
        except Exception as e:
            self.result = 'ServerError'
            
    def SubmittedRecordsOfProblems_Solved(self, result, score, runTime, usingMem):
        try:
            db_session.query(Submissions).\
                filter_by(memberId = self.stdNum,
                          problemId = self.problemNum,
                          courseId = self.courseNum,
                          submissionCount = self.submitCount).\
                update(dict(status = STATUS.index(result),
                            score = score,
                            runTime = runTime,
                            usedMemory = usingMem,
                            solutionCheckCount = Submissions.solutionCheckCount+1))
                
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfSolvedCount = SubmittedRecordsOfProblems.sumOfSolvedCount + 1))
        except Exception as e:
            self.result = 'ServerError'
            raise e
            
    def SubmittedRecordsOfProblems_WrongAnswer(self, result, score, runTime, usingMem):
        try:
            db_session.query(Submissions).\
                filter_by(memberId = self.stdNum,
                          problemId = self.problemNum,
                          courseId = self.courseNum,
                          submissionCount = self.submitCount).\
                update(dict(status = STATUS.index(result),
                            score = score,
                            runTime = runTime,
                            usedMemory = usingMem,
                            solutionCheckCount = Submissions.solutionCheckCount+1))
                
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfWrongCount = SubmittedRecordsOfProblems.sumOfWrongCount + 1))
        except Exception as e:
            self.result = 'ServerError'
            raise e
            
    def SubmittedRecordsOfProblems_TimbeOver(self, result, score, runTime, usingMem):
        try:
            db_session.query(Submissions).\
                filter_by(memberId = self.stdNum,
                          problemId = self.problemNum,
                          courseId = self.courseNum,
                          submissionCount = self.submitCount).\
                update(dict(status = STATUS.index(result),
                            score = score,
                            runTime = runTime,
                            usedMemory = usingMem,
                            solutionCheckCount = Submissions.solutionCheckCount+1))
                
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfTimeOverCount = SubmittedRecordsOfProblems.sumOfTimeOverCount + 1))
        except Exception as e:
            self.result = 'ServerError'
            raise e
            
    def SubmittedRecordsOfProblems_RunTimeError(self, result, score, runTime, usingMem):
        try:
            db_session.query(Submissions).\
                filter_by(memberId = self.stdNum,
                          problemId = self.problemNum,
                          courseId = self.courseNum,
                          submissionCount = self.submitCount).\
                update(dict(status = STATUS.index(result),
                            score = score,
                            runTime = runTime,
                            usedMemory = usingMem,
                            solutionCheckCount = Submissions.solutionCheckCount+1))
                
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfRuntimeErrorCount = SubmittedRecordsOfProblems.sumOfRuntimeErrorCount + 1))
        except Exception as e:
            self.result = 'ServerError'
            raise e
   
    def UpdateServerError(self):
        try :
            db_session.query(Submissions).\
                filter_by(memberId = self.stdNum,
                          problemId = self.problemNum,
                          courseId = self.courseNum,
                          submissionCount = self.submitCount).\
                update(dict(status = 8,
                            score = 0,
                            runTime = 0,
                            usedMemory = 0))
            print '...server error...'
        except Exception as e:
            self.result = 'ServerError'
            raise e