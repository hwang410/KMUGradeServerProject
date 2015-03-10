import os
import sys
from dbinit import databaseInit

if __name__ == '__main__':
    #databaseInit()
    # save system args for list
    args = sys.argv
    
    if len(args) != 12:
        sys.exit()
    else:
        from database import dao
        from DB.submit import Submit
        from grading import InterfaceGrade
        
        os.system('mount -t nfs 192.168.0.119:/mnt/gradeserver /home/algorithm/gradeserver')
        
        grade = InterfaceGrade.InterfaceGrade(args)
        result, stdNum, problemNum, courseNum, submitCount, gradeCount = grade.Compile()
        print result
        
        if result == False:
#             # update database 'compile error'
#             try :
#                 dao.query(Submit).filter_by(memberId = stdNum, problemNum = int(problemNum), courseNum = int(courseNum),\
#                                         submitCount = int(submitCount)).update(dict(status = 3, score = 0, runTime = 0, usingMemory = 0, gradeCount = gradeCount+1))
#                 dao.commit()
#             except Exception as e :
#                 raise e 
#             finally :
#                 dao.remove()
            print '...ing...'
        
        elif result == 'error':
#             # update database 'server error'
#             try :
#                 dao.query(Submit).filter_by(memberId = stdNum, problemNum = int(problemNum), courseNum = int(courseNum),\
#                                         submitCount = int(submitCount)).update(dict(status = 6, score = 0, runTime = 0, usingMemory = 0))
#                 dao.commit()
#             except Exception as e :
#                 raise e 
#             finally :
#                 dao.remove()
            print '...ing...'
        
        else:
            result, runTime = grade.Evaluation()
            print result, runTime
            
            if result == 100:
                # update database 'solved'
#                 try :
#                     dao.query(Submit).filter_by(memberId = stdNum, problemNum = int(problemNum), courseNum = int(courseNum),\
#                                         submitCount = int(submitCount)).update(dict(status = 0, score = 100, runTime = runTime, usingMemory = 0, gradeCount = gradeCount+1))
#                     dao.commit()
#                 except Exception as e :
#                     raise e 
#                 finally :
#                     dao.remove()
                print '...ing...'
            
            elif result == 'time over':
                # update database 'time out'
#                 try :
#                     dao.query(Submit).filter_by(memberId = stdNum, problemNum = int(problemNum), courseNum = int(courseNum),\
#                                         submitCount = int(submitCount)).update(dict(status = 1, score = 0, runTime = runTime, usingMemory = 0, gradeCount = gradeCount+1))
#                     dao.commit()
#                 except Exception as e :
#                     raise e 
#                 finally :
#                     dao.remove()
                print '...ing...'
            
            elif result == 'runtime':
                # update database 'runtime error'
#                 try :
#                     dao.query(Submit).filter_by(memberId = stdNum, problemNum = int(problemNum), courseNum = int(courseNum),\
#                                         submitCount = int(submitCount)).update(dict(status = 4, score = 0, runTime = runTime, usingMemory = 0, gradeCount = gradeCount+1))
#                     dao.commit()
#                 except Exception as e :
#                     raise e 
#                 finally :
#                     dao.remove()
                print '...ing...'
                
            elif result == 'error':
#             # update database 'server error'
#             try :
#                 dao.query(Submit).filter_by(memberId = stdNum, problemNum = int(problemNum), courseNum = int(courseNum),\
#                                         submitCount = int(submitCount)).update(dict(status = 6, score = 0, runTime = 0, usingMemory = 0))
#                 dao.commit()
#             except Exception as e :
#                 raise e 
#             finally :
#                 dao.remove()
                print '...ing...'
            
            else:
                # update database 'wrong answer'
#                 try :
#                     dao.query(Submit).filter_by(memberId = stdNum, problemNum = int(problemNum), courseNum = int(courseNum),\
#                                         submitCount = int(submitCount)).update(dict(status = 2, score = result, runTime = runTime, usingMemory = 0, gradeCount = gradeCount+1))
#                     dao.commit()
#                 except Exception as e :
#                     raise e 
#                 finally :
#                     dao.remove()
                print '...ing...'