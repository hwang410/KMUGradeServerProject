import os
import random
from celery import Celery
from celery import task
from billiard import current_process

MAX_CONTAINER_COUNT = 10
app = Celery('tasks', broker = 'redis://192.168.0.119:6379')

@app.task
def Grade(filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount, limitTime, limitMemory, usingLang, version, courseNum, submitCount):
    argsForm = '%s %s %s %s %s %i %i %i %s %s %s %i'
    argsList = argsForm % (filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount, limitTime, limitMemory,\
                           usingLang, version, courseNum, submitCount)
    random.seed()

    worker_num = current_process().index + 1

    os.system('docker exec grade_container' + str(worker_num) + ' python rungrade.py ' + argsList) 
    
@app.task
def ServerOn():
    for i in range(MAX_CONTAINER_COUNT):
        number = str(i+1)
        os.system('docker create --privileged -i -t --name grade_container' + number + ' gradeserver:1.0 /bin/bash')
        os.system('docker start grade_container' + number)
    
@app.task
def ServerOff():
    for i in range(MAX_CONTAINER_COUNT):
        number = str(i+1)
        os.system('docker stop grade_container' + number)
        os.system('docker rm grade_container' + number)