import os
import sys
from dbinit import DatabaseInit

STATUS = ['grading status', 'NeverSubmitted', 'Judging', 'Solved', 'TimeOver',
          'WrongAnswer', 'CompileError', 'RunTimeError', 'ServerError']

if __name__ == '__main__':
    # databate initialization
    DatabaseInit()
    
    # save system args for list
    args = sys.argv
    
    if len(args) != 14:
        sys.exit()
    
    from database import dao
    from DB.submissions import Submissions
    from DB.submittedRecordsOfProblems import SubmittedRecordsOfProblems
    from grading import InterfaceGrade
    
    os.chdir('temp')
    os.system('rm -r *')
    
    grade = InterfaceGrade.InterfaceGrade(args)
    result, stdNum, problemNum, courseNum, submitCount = grade.Compile()
    print result
    
    if not result:
        # update database 'compile error'
        try :
            dao.query(Submissions).\
                filter_by(memberId = stdNum,
                          problemId = problemNum,
                          courseId = courseNum,
                          submissionCount = submitCount).\
                update(dict(status = 6,
                            score = 0,
                            runTime = 0,
                            usedMemory = 0,
                            solutionCheckCount = Submissions.solutionCheckCount + 1))
            
            dao.query(SubmittedRecordsOfProblems).\
                filter_by(problemId = problemNum,
                          courseId = courseNum).\
                update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                            sumOfCompileErrorCount = SubmittedRecordsOfProblems.sumOfCompileErrorCount + 1))
            
            dao.commit()
            
            print '...compile error...'
            sys.exit()
        except Exception as e :
            dao.rollback()
            result = 'ServerError'
            raise e
        
    
    if result == 'ServerError':
        # update database 'server error'
        try :
            dao.query(Submissions).\
                filter_by(memberId = stdNum,
                          problemId = problemNum,
                          courseId = courseNum,
                          submissionCount = submitCount).\
                update(dict(status = 8,
                            score = 0,
                            runTime = 0,
                            usedMemory = 0))
            dao.commit()
            
            print '...compile server error...'
            sys.exit()
        except Exception as e :
            dao.rollback()
            raise e 
    
    else:
        result, score, runTime, usingMem = grade.Evaluation()
        print result, score, runTime, usingMem
        
                    # update database 'solved'
        try:
            dao.query(Submissions).\
                filter_by(memberId = stdNum,
                          problemId = problemNum,
                          courseId = courseNum,
                          submissionCount = submitCount).\
                update(dict(status = STATUS.index(result),
                            score = score,
                            runTime = runTime,
                            usedMemory = usingMem,
                            solutionCheckCount = Submissions.solutionCheckCount+1))
            
            dao.commit()
        except Exception as e:
            result = 'ServerError'
            dao.rollback() 
            raise e
            
        if result == 'Solved':
            # update database 'solved'
            try:
                dao.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = problemNum,
                              courseId = courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfSolvedCount = SubmittedRecordsOfProblems.sumOfSolvedCount + 1))
                
                dao.commit()
                
                print '...solved...'
                sys.exit()
            except Exception as e:
                result = 'ServerError'
                dao.rollback()
                raise e
        
        elif result == 'TimeOver':
            # update database 'time out'
            try:
                dao.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = problemNum,
                              courseId = courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfTimeOverCount = SubmittedRecordsOfProblems.sumOfTimeOverCount + 1))
                
                dao.commit()
                
                print '...time over...'
                sys.exit()
            except Exception as e:
                result = 'ServerError'
                dao.rollback()
                raise e
        
        elif result == 'RunTimeError':
            # update database 'runtime error'
            try:
                dao.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = problemNum,
                              courseId = courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfRuntimeErrorCount = SubmittedRecordsOfProblems.sumOfRuntimeErrorCount + 1))
                
                dao.commit()
                
                print '...runtime error...'
                sys.exit()
            except Exception as e:
                result = 'ServerError'
                dao.rollback()
                raise e
        
        elif result == 'WrongAnser':
            # update database 'wrong answer'
            try:
                dao.query(SubmittedRecordsOfProblems).\
                    filter_by(problemId = problemNum,
                              courseId = courseNum).\
                    update(dict(sumOfSubmissionCount = SubmittedRecordsOfProblems.sumOfSubmissionCount + 1,
                                sumOfWrongCount = SubmittedRecordsOfProblems.sumOfWrongCount + 1))
                
                dao.commit()
                
                print '...wrong answer...'
                sys.exit()
            except Exception as e:
                result = 'ServerError'
                dao.rollback()
                raise e
            
        if result == 'ServerError':
        # update database 'server error'
            try :
                dao.query(Submissions).\
                    filter_by(memberId = stdNum,
                              problemId = problemNum,
                              courseId = courseNum,
                              submissionCount = submitCount).\
                    update(dict(status = 8,
                                score = 0,
                                runTime = 0,
                                usedMemory = 0))
                dao.commit()
                print '...execution server error...'
            except Exception as e:
                dao.rollback()
                raise e 