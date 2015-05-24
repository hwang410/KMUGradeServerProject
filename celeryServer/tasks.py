from __future__ import absolute_import
from celeryServer import app

import os
import time
import DBUpdate
from subprocess import Popen, PIPE
from billiard import current_process

MAX_CONTAINER_COUNT = 4
ROOT_CONTAINER_DIRECTORY = '/container'

@app.task(name = 'task.Grade')
def Grade(filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount,
          limitTime, limitMemory, usingLang, version, courseNum, submitCount, problemName):
    worker_num = current_process().index % MAX_CONTAINER_COUNT + 1
    
    saveDirectoryName = "%s%s%s%i" % (stdNum, problemNum, courseNum, submitCount)
    sharingDirName = "%s%i/%s" % (ROOT_CONTAINER_DIRECTORY, worker_num,
                            saveDirectoryName)
    argsList = "%s %s %s %s %i %i %i %s %s %s" % (filePath, problemPath,
                                                  saveDirectoryName, gradeMethod,
                                                  caseCount, limitTime,
                                                  limitMemory, usingLang,
                                                  version, problemName)
    containerCommand = "%s%i%s" % ('sudo docker exec grade_container', worker_num,
                                   ' python /gradeprogram/rungrade.py ')

    
    os.system('sudo mkdir ' + sharingDirName)
    print 'program start'
    message = Popen(containerCommand + argsList, shell=True, stdout=PIPE)
    
    while message.poll() == None:
        time.sleep(0.01)
    
    messageLines = message.stdout.readlines()
    os.system('sudo rm -rf ' + sharingDirName)
    
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
    dataUpdate = DBUpdate.DBUpdate(stdNum, problemNum, courseNum, submitCount)
    messageParaList = messageLine.split() 
    
    if len(messageParaList) != 4:
        dataUpdate.UpdateServerError()
    
    result = messageParaList[0]
    score = messageParaList[1]
    runTime = messageParaList[2]
    usingMem = messageParaList[3]
    
    if result == 'WrongAnswer':
        dataUpdate.SubmittedRecordsOfProblems_WrongAnswer(result, score, runTime, usingMem)
    
    elif result == 'TimeOver':
        dataUpdate.SubmittedRecordsOfProblems_TimbeOver(result, score, runTime, usingMem)
    
    elif result == 'Solved':
        dataUpdate.SubmittedRecordsOfProblems_Solved(result, score, runTime, usingMem)
        
    elif result == 'RunTimeError':
        dataUpdate.SubmittedRecordsOfProblems_RunTimeError(result, score, runTime, usingMem)
        
    elif result == 'CompileError':
        dataUpdate.SubmittedRecordsOfProblems_CompileError(result, score, runTime, usingMem)
        
    else:
        dataUpdate.UpdateServerError()