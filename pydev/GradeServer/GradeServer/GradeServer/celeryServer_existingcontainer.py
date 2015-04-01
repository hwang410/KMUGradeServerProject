import os
import random
from celery import Celery
from celery import task
from billiard import current_process
app = Celery('tasks', broker = 'redis://192.168.0.119:6379')

@app.task
def Grade(filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount, limitTime, limitMemory, usingLang, version, courseNum, submitCount):
    argsForm = '%s %s %s %i %s %i %i %i %s %s %i %i'
    argsList = argsForm % (filePath, problemPath, stdNum, problemNum, gradeMethod, caseCount, limitTime, limitMemory,\
                           usingLang, version, courseNum, submitCount)
    random.seed()

#    containerName = str(stdNum + random.randrange(100, 999) + problemNum)
           worker_num = current_process().index + 1

#    os.system('docker run --privileged=true -i -t --name ' + containerName + ' --rm=true grade:1.0 python rungrade.py ' + argsList)
    os.system('docker exec grade_container' + str(worker_num) + ' python rungrade.py ' + argsList) 
