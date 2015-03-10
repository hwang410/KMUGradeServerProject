import os
import threading

class runThread(threading.Thread):
    def __init__(self, runCommand, stdNum):
        threading.Thread.__init__(self)
        self.runCommand = runCommand
        self.stdNum = stdNum
        
    def run(self):
        os.system(self.runCommand)
        
    def shutdown(self, stdNum):
        cmd = 'killall -9 ' + stdNum
        os.system(cmd)