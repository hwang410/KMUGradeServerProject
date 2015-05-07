from __future__ import absolute_import
from celeryServer import app

import os
import time
import DBUpdate
from DBManager import db_session, engine
from subprocess import Popen, PIPE
from billiard import current_process

MAX_CONTAINER_COUNT = 4

@app.task(name = 'task.Grade')
def Grade(filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount,
          limitTime, limitMemory, usingLang, version, courseNum, submitCount, problemName):
    worker_num = current_process().index % MAX_CONTAINER_COUNT + 1
    
    argsList = "%s %s %s %s %s %i %i %i %s %s %s %i %s" % (filePath, problemPath,
                                                           stdNum, problemNum,
                                                           gradeMethod, caseCount,
                                                           limitTime, limitMemory,
                                                           usingLang, version,
                                                           courseNum, submitCount,
                                                           problemName)
    containerCreadeCommand = "%s%i%s" % ('sudo docker exec grade_container',
                                         worker_num,
                                         ' python /gradeprogram/rungrade.py ')

    print 'program start'
    message = Popen(containerCreadeCommand + argsList, shell=True, stdout=PIPE)
    
    messageLines = message.stdout.readlines()
    
    resultUpdate(messageLines[-1], stdNum, problemNum, courseNum, submitCount)
    
@app.task(name = 'task.ServerOn')
def ServerOn():
    for i in range(MAX_CONTAINER_COUNT):
        containerNum = i + 1
        containerCreadeCommand = "%s%i%s%i%s" %('sudo docker create --privileged -i -t --name --cpuset="',
                                                i, '" grade_container', containerNum,
                                                ' gradeserver:1.0 /bin/bash')
        
        runProgramInContainer = '%s%i%s' % ('sudo docker exec grade_container',
                                            containerNum, 'python -B /gradeprogram/*')
        os.system(containerCreadeCommand)
        os.system('sudo docker start grade_container' + containerNum)
        os.system(runProgramInContainer)
    
@app.task(name = 'task.ServerOff')
def ServerOff():
    time.sleep(5)
    
    for i in range(MAX_CONTAINER_COUNT):
        number = str(i+1)
        os.system('sudo docker stop grade_container' + number)
        os.system('sudo docker rm grade_container' + number)
        
def resultUpdate(messageLine, stdNum, problemNum, courseNum, submitCount):        
    messageParaList = messageLine.split() 
    
    result = messageParaList[0]
    score = messageParaList[1]
    runTime = messageParaList[2]
    usingMem = messageParaList[3]
    
    dataUpdate = DBUpdate.DBUpdate(stdNum, problemNum, courseNum, submitCount)
    
    dataUpdate.UpdateSubmissions(result, score, runTime, usingMem)
     
    if result == 'Solved':
    # update DBManager 'solved'
        dataUpdate.SubmittedRecordsOfProblems_Solved()
     
    elif result == 'TimeOver':
    # update DBManager 'time out'
        dataUpdate.SubmittedRecordsOfProblems_TimbeOver()
     
    elif result == 'RunTimeError':
    # update DBManager 'runtime error'
        dataUpdate.SubmittedRecordsOfProblems_RunTimeError()
     
    elif result == 'WrongAnswer':
    # update DBManager 'wrong answer'
        dataUpdate.SubmittedRecordsOfProblems_WrongAnswer()
        
    elif result == 'CompileError':
        dataUpdate.SubmittedRecordsOfProblems_CompileError()
        
    else:
        dataUpdate.UpdateServerError(stdNum, problemNum,
                                   courseNum, submitCount)