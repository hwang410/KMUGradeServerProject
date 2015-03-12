import os
import threading

class runThread(threading.Thread):
    def __init__(self, runCommand, runFileName):
        threading.Thread.__init__(self)
        self.runCommand = runCommand
        self.runFileName = runFileName
        
    def run(self):
        os.system(self.runCommand)
        
    def shutdown(self):
        cmd = 'killall -9 ' + self.runFileName
        os.system(cmd)