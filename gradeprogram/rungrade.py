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
        os.chdir('temp')
        
        grade = InterfaceGrade.InterfaceGrade(args)
        result, stdNum, problemNum, courseNum, submitCount = grade.Compile()
        print result
        
        if result == False:
            # update database 'compile error'
            try :
                dao.query(Submissions).filter_by(memberId = stdNum, problemId = problemNum, courseId = courseNum,\
                                        submissionCount = submitCount).update(dict(status = 6, score = 0, runTime = 0,\
                                                                                        usedMemory = 0, solutionCheckCount = Submissions.solutionCheckCount + 1))
                
                dao.query(SubmittedRecordsOfProblems).filter_by(problemId = problemNum, courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfCompileErrorCount = SubmittedRecordsOfProblems.sumOfCompileErrorCount + 1))
                
                dao.commit()
            except Exception as e :
                raise e
                result = 'error'
                dao.rollback()
            
            print '...compile error...'
        
        elif result == 'error':
            # update database 'server error'
            try :
                dao.query(Submissions).filter_by(memberId = stdNum, problemId = problemNum, courseId = courseNum,\
                                        submissionCount = submitCount).update(dict(status = 8, score = 0, runTime = 0, usedMemory = 0))
                dao.commit()
            except Exception as e :
                raise e 
                dao.rollback()
            
            print '...compile server error...'
        
        else:
            result, runTime, usingMem = grade.Evaluation()
            print result, runTime, usingMem
            
            if result == 100:
                # update database 'solved'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = problemNum, courseId = courseNum,\
                                        submissionCount = submitCount).update(dict(status = 3, score = 100, runTime = runTime,\
                                                                                   usedMemory = usingMem,\
                                                                                   solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = problemNum, courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfSolvedCount = SubmittedRecordsOfProblems.sumOfSolvedCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e
                    result = 'error'
                    dao.rollback() 
                    
                print '...solved...'
            
            elif result == 'time over':
                # update database 'time out'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = problemNum, courseId = courseNum,\
                                        submissionCount = submitCount).update(dict(status = 4, score = 0, runTime = runTime,\
                                                                                        usedMemory = usingMem,\
                                                                                        solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = problemNum, courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfTimeOverCount = SubmittedRecordsOfProblems.sumOfTimeOverCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e 
                    result = 'error'
                    dao.rollback()
                    
                print '...time over...'
            
            elif result == 'runtime':
                # update database 'runtime error'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = problemNum, courseId = courseNum,\
                                        submissionCount = submitCount).update(dict(status = 7, score = 0, runTime = runTime,\
                                                                                        usedMemory = usingMem,\
                                                                                        solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = problemNum, courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfRuntimeErrorCount = SubmittedRecordsOfProblems.sumOfRuntimeErrorCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e
                    result = 'error'
                    dao.rollback()
                
                print '...runtime error...'
            
            elif result < 100:
                # update database 'wrong answer'
                try:
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = problemNum, courseId = courseNum,\
                                        submissionCount = submitCount).update(dict(status = 5, score = result, runTime = runTime,\
                                                                                        usedMemory = usingMem,\
                                                                                        solutionCheckCount = Submissions.solutionCheckCount+1))
                    
                    dao.query(SubmittedRecordsOfProblems).filter_by(problemId = problemNum, courseId = courseNum).\
                            update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,\
                                        sumOfWrongCount = SubmittedRecordsOfProblems.sumOfWrongCount + 1))
                    
                    dao.commit()
                except Exception as e:
                    raise e 
                    result = 'error'
                    dao.rollback()
                
                print '...wrong answer...'
                
            elif result == 'error':
            # update database 'server error'
                try :
                    dao.query(Submissions).filter_by(memberId = stdNum, problemId = problemNum, courseId = courseNum,\
                                        submissionCount = submitCount).update(dict(status = 8, score = 0, runTime = 0, usedMemory = 0))
                    dao.commit()
                except Exception as e:
                    raise e 
                    dao.rollback()
                
                print '...execution server error...'