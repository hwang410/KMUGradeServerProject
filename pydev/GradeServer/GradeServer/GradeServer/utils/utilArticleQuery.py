
# -*- coding: utf-8 -*-

from sqlalchemy import func

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.model.submissions import Submissions
from GradeServer.model.problems import Problems
from GradeServer.model.members import Members
from GradeServer.model.departments import Departments
from GradeServer.model.languages import Languages
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.colleges import Colleges