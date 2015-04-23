from subprocess import call

class GradingTools(object):
    def __init__(self, gradeMethod, caseCount, usingLang, version, answerPath,
                 problemName, filePath):
        self.gradeMethod =gradeMethod 
        self.caseCount = caseCount
        self.usingLang = usingLang
        self.version = version
        self.answerPath = answerPath
        self.problemName = problemName
        self.filePath = filePath
        
    def Grade(self):
        if self.gradeMethod == 'Solution':   # solution
            if self.caseCount > 1:
                result, score = self.SolutionMulti()
                
            else:
                result, score = self.SolutionSingle()
            
        else:   # checker
            if self.caseCount > 1:
                result, score = self.CheckerMulti()
                
            else:
                result, score = self.CheckerSingle()
            
        return result, score
    
    def MakeMulticaseCommand(self):
        # make execution command
        if self.usingLang == 'PYTHON':
            if self.version == '2.7':
                return 'python ' + self.runFileName + '.py 1>output.txt 2>core.1'
            elif self.version == '3.4':
                return 'python3 ' + self.runFileName + '.py 1>output.txt 2>core.1'
        
        elif self.usingLang == 'C' or self.usingLang == 'C++':
            return 'ulimit -c unlimited; ./main 1>output.txt'
        
        elif self.usingLang == 'JAVA':
            return 'java ' + self.runFileName + ' 1>output.txt 2>core.1'
        
    def SolutionSingle(self):
        # user output file each line compare with answer file each line.
        try:
            answerFile = open(self.answerPath + self.problemName + '_cases_total_outputs.out', 'r')
            stdOutput = open('output.txt', 'r')
        except Exception as e:
            print e
            return 'error'
        
        stdLines = stdOutput.readlines()
        answerLines = answerFile.readlines()
        
        answerFile.close()
        stdOutput.close()
        
        count = len(stdLines) - len(answerLines)
        
        _min = len(stdLines) if count < 0 else len(answerLines)
        count = abs(count)
        
        for i in range(_min):
            stdLine = stdLines[i].strip('\r\n')
            answerLine = answerLines[i].strip('\r\n')
            
            if stdLine != answerLine:   # if not same each line
                count += 1
        
        result = 'Solved'
        score = 100
        
        if count > 0:
            result = 'WrongAnswer'
            score = int( ((len(answerLines) - count) * 100) / len(answerLines) )
            
        if score < 0:
            return 'WrongAnswer', 0
            
        return result, score
        
    def CheckerSingle(self):
        try:
            call('cp ' + self.answerPath + self.problemName + '.out checker.out', shell = True)
            call('./checker.out 1>result.txt', shell = True)
        except Exception as e:
            print e
            return 'error'
        
        rf = open('reuslt.txt', 'r')
        
        score = rf.readline()
        
        rf.close()
        
        return int(score)
    
    def SolutionMulti(self):
        count = 0
        _list = []
        
        command = self.MakeMulticaseCommand()
        
        for i in range(1, self.caseCount+1):
            try:
                # input.txt file copy
                call('rm -r input.txt', shell = True)
                call('cp ' + self.answerPath + self.problemName + '_case' + str(i) +
                     '_input.in input.txt', shell = True)
                
                # program run
                call(command, shell = True)
            
                answerFile = open(self.answerPath + self.problemName + '_case' + str(i) +
                                  '_output.out', 'r') # answer output open
                stdOutput = open('output.txt', 'r') # student output open
            except Exception as e:
                print e
                return 'error'
            
            answer = answerFile.read()
            student = stdOutput.read()
            
            answerFile.close()
            stdOutput.close()
            
            answer = answer.strip('\r\n')
            student = student.strip('\r\n')
            
            if answer != student:
                count += 1
                _list.append(i)
           
        if count == 0:
            return 100
        
        else:
            self.MakeCaseList(_list)
            return int( ((self.caseCount - count) * 100) / self.caseCount )
        
    def CheckerMulti(self):
        count = 0
        _list = []
        
        command = self.MakeMulticaseCommand()
        
        try:
            call('cp ' + self.answerPath + self.problemName + '.out checker.out', shell = True)
        except Exception as e:
                print e
                return 'error'    
        
        for i in range(1, self.caseCount+1):
            try:
                # input.txt file copy
                call('rm -r input.txt', shell = True)
                call(self.answerPath + self.problemName + '_case' + str(i) +
                     '_input.in input.txt', shell = True)
                
                # program run
                call(command, shell = True)
            
                call('./checker.out 1>result.txt', shell = True)
                rf = open('reuslt.txt', 'r')
            except Exception as e:
                print e
                return 'error'
            
            score = rf.readline()
            
            rf.close()
            
            if int(score) != 100:
                count += 1
                _list.append(i)
           
        if count == 0:
            return 100
        
        else:
            self.MakeCaseList(_list)
            return int( ((self.caseCount - count) * 100) / self.caseCount )
        
    def MakeCaseList(self, _list):
        wf = open(self.filePath + 'caselist.txt', 'w')
        size = len(_list)
            
        wf.wrtie(str(size))
            
        for i in size:
            rf = open(self.answerPath + self.problemName + '_case' + str(_list[i]) + '.in', 'r')
            case = rf.readlines()
            rf.close()
                
            if case[-1].find('\n'):
                case[-1] = case[-1] + '\n'
                
            wf.write(case)
                
        wf.close()