from DBManager import db_session
from DB.submissions import Submissions
from gradingResource.enumResources import ENUMResources
from gradingResource.listResources import ListResources
from DB.submittedRecordsOfProblems import SubmittedRecordsOfProblems

class DBUpdate(object):
    def __init__(self, stdNum, problemNum, courseNum, submitCount):
        self.stdNum = stdNum
        self.problemNum = problemNum
        self.courseNum = courseNum
        self.submitCount = submitCount
        
    def UpdateResutl(self, messageParaList):
        try:
            if len(messageParaList) != 4:
                self.UpdateServerError()
                return
                
            else:
                result = messageParaList[0]
                score = messageParaList[1]
                runTime = messageParaList[2]
                usingMem = messageParaList[3]
            
                if result == ENUMResources.const.WRONG_ANSWER:
                    self.UpdateTable_SubmittedRecordsOfProblems_WrongAnswer()
                
                elif result == ENUMResources.const.TIME_OVER:
                    self.UpdateTable_SubmittedRecordsOfProblems_TimbeOver()
                
                elif result == ENUMResources.const.SOLVED:
                    self.UpdateTable_SubmittedRecordsOfProblems_Solved()
                    
                elif result == ENUMResources.const.RUNTIME_ERROR:
                    self.UpdateTable_SubmittedRecordsOfProblems_RunTimeError()
                    
                elif result == ENUMResources.const.COMPILE_ERROR:
                    self.UpdateTable_SubmittedRecordsOfProblems_CompileError()
                    
                else:
                    self.UpdateServerError()
                    return
                
                self.UpdateTableSubmissions(result, score, runTime, usingMem)
                
                db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.UpdateServerError()
            
    
    def UpdateTableSubmissions(self, result, score, runTime, usingMem):
        try:
            db_session.query(Submissions).\
                filter_by(memberId = self.stdNum,
                          problemId = self.problemNum,
                          courseId = self.courseNum,
                          submissionCount = self.submitCount).\
                update(dict(status = ListResources.const.GRADERESULT_List.index(result),
                            score = score,
                            runTime = runTime,
                            usedMemory = usingMem,
                            solutionCheckCount = Submissions.solutionCheckCount+1))
        except Exception as e:
            raise e
    
    def UpdateTable_SubmittedRecordsOfProblems_CompileError(self):
        try:
            db_session.query(SubmittedRecordsOfProblems).\
                filter_by(problemId = self.problemNum,
                          courseId = self.courseNum).\
                          update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                      sumOfCompileErrorCount = SubmittedRecordsOfProblems.sumOfCompileErrorCount + 1))
        except Exception as e:
            raise e
            
    def UpdateTable_SubmittedRecordsOfProblems_Solved(self):
        try:
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfSolvedCount = SubmittedRecordsOfProblems.sumOfSolvedCount + 1))
        except Exception as e:
            raise e
            
    def UpdateTable_SubmittedRecordsOfProblems_WrongAnswer(self):
        try:
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfWrongCount = SubmittedRecordsOfProblems.sumOfWrongCount + 1))
        except Exception as e:
            raise e
            
    def UpdateTable_SubmittedRecordsOfProblems_TimbeOver(self):
        try:
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfTimeOverCount = SubmittedRecordsOfProblems.sumOfTimeOverCount + 1))
        except Exception as e:
            raise e
            
    def UpdateTable_SubmittedRecordsOfProblems_RunTimeError(self):
        try:
            db_session.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = self.problemNum,
                              courseId = self.courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfRuntimeErrorCount = SubmittedRecordsOfProblems.sumOfRuntimeErrorCount + 1))
        except Exception as e:
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
            db_session.commit()
            print '...server error...'
        except Exception as e:
            raise e