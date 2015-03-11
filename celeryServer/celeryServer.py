import os
import random
from celery import Celery

MAX_CONTAINER_COUNT = 7

app = Celery('tasks', broker = 'redis://192.168.0.118:6379')

@app.task
def Grade(courseName, stdNum, problemNum, gradeMethod, limitTime, caseCount, usingLang, version, courseNum, submitCount):
    argsForm = '%s %s %s %s %s %s %s %s %s %s'
    argsList = argsForm % (courseName +  stdNum, problemNum, gradeMethod, limitTime, caseCount, usingLang, version, courseNum, submitCount)
    random.seed()
    
    while(1):
        os.system('docker ps -a 1>count.txt')
   
        rf = open('count.txt', 'r') 
   
        lines = rf.readlines()
       
        if len(lines) < MAX_CONTAINER_COUNT + 1:
            rf.cloase()
            break;
        
        rf.close()
        
    pid = os.fork()
    
    if pid == 0:
        containerName = str(random.randrange(1000, 9999)) + stdNum + str(random.randrange(1000, 9999) + problemNum)
       
        os.system('docker run --privileged=true -i -t --name ' + containerName + ' --rm=true grade:1.0 python rungrade.py ' + argsList)