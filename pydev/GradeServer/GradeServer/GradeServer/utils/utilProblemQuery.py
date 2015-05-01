# -*- coding: utf-8 -*-

from sqlalchemy import and_, func

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
Get Problems
'''
def select_problem(courseId):
    return dao.query(RegisteredProblems).\
               filter(RegisteredProblems.courseId == courseId)


'''
Join Problem Names
'''
def join_problem_name(registeredProblems):
    return dao.query(registeredProblems,
                     Problems.problemName).\
               join(Problems,
                    registeredProblems.c.problemId == Problems.problemId)


