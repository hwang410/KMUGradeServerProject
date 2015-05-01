import os
import time
from celery import Celery
from billiard import current_process

MAX_CONTAINER_COUNT = 4
app = Celery('tasks', broker = 'redis://192.168.0.8:6379')

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

    os.system(containerCreadeCommand + argsList) 
    
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