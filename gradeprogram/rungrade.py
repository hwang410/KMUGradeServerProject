import os
import sys

if __name__ == '__main__':
    # save system args for list
    args = sys.argv
    
    if len(args) != 14:
        sys.exit()
    
    from grading import InterfaceGrade
    
    os.chdir('temp')
    os.system('rm -r *')
    
    grade = InterfaceGrade.InterfaceGrade(args)
    result, stdNum, problemNum, courseNum, submitCount = grade.Compile()
    
    # create DB update object 
#     dataUpdate = DBUpdate.DBUpdate(stdNum, problemNum, courseNum, submitCount)
    
    if result == 'CompileError':
        # update DBManager 'compile error'
        print result, 0, 0, 0
        sys.exit()
#         dataUpdate.UpdateSubmissions(result, 0, 0, 0)
#             
#         dataUpdate.SubmittedRecordsOfProblems_CompileError()
    
    
    result, score, runTime, usingMem = grade.Evaluation()
    
    # update DBManager 'solved'
    print result, score, runTime, usingMem
#     dataUpdate.UpdateSubmissions(result, score, runTime, usingMem)
#     
#     if result == 'Solved':
#     # update DBManager 'solved'
#         dataUpdate.SubmittedRecordsOfProblems_Solved()
#     
#     elif result == 'TimeOver':
#     # update DBManager 'time out'
#         dataUpdate.SubmittedRecordsOfProblems_TimbeOver()
#     
#     elif result == 'RunTimeError':
#     # update DBManager 'runtime error'
#         dataUpdate.SubmittedRecordsOfProblems_RunTimeError()
#     
#     elif result == 'WrongAnswer':
#     # update DBManager 'wrong answer'
#         dataUpdate.SubmittedRecordsOfProblems_WrongAnswer()
#     else:
#         dataUpdate.UpdateServerError(stdNum, problemNum,
#                                    courseNum, submitCount)