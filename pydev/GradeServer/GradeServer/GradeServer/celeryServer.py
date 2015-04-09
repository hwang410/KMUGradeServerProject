import os
import time
from celery import Celery
from billiard import current_process

MAX_CONTAINER_COUNT = 10
app = Celery('tasks', broker = 'redis://192.168.0.8:6379')

@app.task(name = 'task.Grade')
def Grade(filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount, limitTime, limitMemory, usingLang, version, courseNum, submitCount):
    argsForm = '%s %s %s %s %s %i %i %i %s %s %s %i'
    argsList = argsForm % (filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount, limitTime, limitMemory,\
                           usingLang, version, courseNum, submitCount)

    worker_num = current_process().index + 1

    os.system('sudo docker exec grade_container' + str(worker_num) + ' python /gradeprogram/rungrade.py ' + argsList) 
    
@app.task(name = 'task.ServerOn')
def ServerOn():
    for i in range(MAX_CONTAINER_COUNT):
        number = str(i+1)
        os.system('sudo docker create --privileged -i -t --name grade_container' + number + ' gradeserver:1.0 /bin/bash')
        os.system('sudo docker start grade_container' + number)
    
@app.task(name = 'task.ServerOff')
def ServerOff():
    time.sleep(5)
    
    for i in range(MAX_CONTAINER_COUNT):
        number = str(i+1)
        os.system('sudo docker stop grade_container' + number)
        os.system('sudo docker rm grade_container' + number)