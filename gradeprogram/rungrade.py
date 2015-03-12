import sys
from dbinit import databaseInit

if __name__ == '__main__':
    # databate initialization
    databaseInit()
    
    # save system args for list
    args = sys.argv
    
    if len(args) != 13:
        sys.exit()
    else:
        import os
        from database import dao
        from DB.submissions import Submissions
        from DB.submittedRecordsOfProblems import SubmittedRecordsOfProblems
        from grading import InterfaceGrade
        
        #os.mkdir('temp')
        #os.chdir('temp')
        
        grade = InterfaceGrade.InterfaceGrade(args)
        result, stdNum, problemNum, courseNum, submitCount = grade.Compile()
        print result
        
        if result == False:
            # update database 'compile error'
            try :
                dao.query(Submissions).filter_by(memberId = stdNum, problemId = int(problemNum), courseId = courseNum,\
                                        submissionCount = int(submitCount)).update(dict(status = 5, score = 0, runTime = 0,\
                                                                                        usedMemory = 0, solutionCheckCount = Submissions.solutionCheckCount + 1))
                
                dao.query(SubmittedRecordsOfProblems).filter_by(problemId = int(problemNum), courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfCompileErrorCount = SubmittedRecordsOfProblems.sumOfCompileErrorCount + 1))
                
                dao.commit()
            except Exception as e :
                raise e 
            finally:
                dao.remove()
            print '...compile error...'
        
        elif result == 'error':
            # update database 'server error'
            try :
                dao.query(Submissions).filter_by(memberId = stdNum, problemId = int(problemNum), courseId = courseNum,\
                                        submissionCount = int(submitCount)).update(dict(status = 7, score = 0, runTime = 0, usedMemory = 0))
                dao.commit()
            except Exception as e :
                raise e 
            finally:
                dao.remove()
            print '...compile server error...'
        
        else:
            result, runTime = grade.Evaluation()
            print result, runTime
            
            if result == 100:
                # update database 'solved'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = int(problemNum), courseId = courseNum,\
                                        submissionCount = int(submitCount)).update(dict(status = 2, score = 100, runTime = runTime,\
                                                                                        usedMemory = 0, solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = int(problemNum), courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfSolvedCount = SubmittedRecordsOfProblems.sumOfSolvedCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e 
                finally:
                    dao.remove()
                print '...solved...'
            
            elif result == 'time over':
                # update database 'time out'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = int(problemNum), courseId = courseNum,\
                                        submissionCount = int(submitCount)).update(dict(status = 3, score = 0, runTime = runTime,\
                                                                                        usedMemory = 0, solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = int(problemNum), courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfTimeOverCount = SubmittedRecordsOfProblems.sumOfTimeOverCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e 
                finally:
                    dao.remove()
                print '...time over...'
            
            elif result == 'runtime':
                # update database 'runtime error'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = int(problemNum), courseId = courseNum,\
                                        submissionCount = int(submitCount)).update(dict(status = 6, score = 0, runTime = runTime,\
                                                                                        usedMemory = 0, solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = int(problemNum), courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOFRuntimeErrorCount = SubmittedRecordsOfProblems.sumOfRuntimeErrorCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e 
                finally:
                    dao.remove()
                print '...rumtime error...'
                
            elif result == 'error':
            # update database 'server error'
                try :
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = int(problemNum), courseId = courseNum,\
                                        submissionCount = int(submitCount)).update(dict(status = 7, score = 0, runTime = 0, usedMemory = 0))
                    dao.commit()
                except Exception as e:
                    raise e 
                finally:
                    dao.remove()
                print '...execution server error...'
            
            else:
                # update database 'wrong answer'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = int(problemNum), courseId = courseNum,\
                                        submissionCount = int(submitCount)).update(dict(status = 4, score = result, runTime = runTime,\
                                                                                        usedMemory = 0, solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = int(problemNum), courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfWrongCount = SubmittedRecordsOfProblems.sumOfWrongCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e 
                finally:
                    dao.remove()
                print '...wrong answer...'