from subprocess import call
import threading

class runThread(threading.Thread):
    def __init__(self, runCommand, runFileName):
        threading.Thread.__init__(self)
        self.runCommand = runCommand
        self.runFileName = runFileName
        
    def run(self):
        call(self.runCommand, shell=True)
        
    def shutdown(self):
        cmd = 'killall -9 ' + self.runFileName
        call(cmd, shell=True)