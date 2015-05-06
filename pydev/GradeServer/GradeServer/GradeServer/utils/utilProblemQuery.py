# -*- coding: utf-8 -*-

from sqlalchemy import and_, func

from datetime import datetime

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer

from GradeServer.model.registeredProblems import RegisteredProblems
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.problems import Problems
from GradeServer.model.submissions import Submissions
from GradeServer.model.submittedFiles import SubmittedFiles
from GradeServer.model.submittedRecordsOfProblems import SubmittedRecordsOfProblems
from GradeServer.model.languages import Languages
from GradeServer.model.languagesOfCourses import LanguagesOfCourses
from GradeServer.model.problems import Problems


'''
Get Problem Information
'''
def select_problem_informations(problemId):
    return dao.query(Problems).\
               filter(Problems.problemId == problemId)
               
               
               
'''
Get Problems of Course
'''
def select_problems_of_course(courseId, problemId = None):
    return dao.query(RegisteredProblems).\
               filter(RegisteredProblems.courseId == courseId,
                      (RegisteredProblems.problemId == problemId if problemId
                       else RegisteredProblems.openDate <= datetime.now()))


'''
Join Problem Names
'''
def join_problems_names(registeredProblems):
    return dao.query(registeredProblems,
                     Problems.problemName).\
               join(Problems,
                    registeredProblems.c.problemId == Problems.problemId)


'''
OuterJoin Problem List and submission_code
'''
def join_problem_lists_submissions(problems, submissions):
    return dao.query(problems,
                     submissions.c.score,
                     submissions.c.status,
                     submissions.c.submissionCount,
                   submissions.c.solutionCheckCount).\
               outerjoin(submissions,
                         problems.c.problemId == submissions.c.problemId).\
               order_by(problems.c.startDateOfSubmission.desc())
   

'''
Submission code View Counting
'''
def update_submission_code_view_count(lastSubmission, memberId, courseId, problemId):
    dao.query(Submissions).\
        filter(Submissions.memberId == memberId,
               Submissions.courseId == courseId,
               Submissions.problemId == problemId,
               Submissions.submissionCount == lastSubmission.c.submissionCount).\
        update(dict(viewCount = Submissions.viewCount + 1))