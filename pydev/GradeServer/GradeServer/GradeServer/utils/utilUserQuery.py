
# -*- coding: utf-8 -*-

from GradeServer.database import dao

from GradeServer.model.departments import Departments
from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.colleges import Colleges

'''
Update Member Information
'''
def update_member_information(members, password, contactNumber, emailAddress, comment):
    members.update(dict(password = password,
                        contactNumber = contactNumber,
                        emailAddress = emailAddress,
                        comment = comment))
    
                    
'''
Join Members, College, Departments
'''
def join_member_information(members):
    return dao.query(members,
                     Colleges.collegeName,
                     Departments.departmentName).\
               outerjoin(DepartmentsDetailsOfMembers,
                         members.c.memberId == DepartmentsDetailsOfMembers.memberId).\
               outerjoin(Colleges,
                         Colleges.collegeIndex == DepartmentsDetailsOfMembers.collegeIndex).\
               outerjoin(Departments,
                         Departments.departmentIndex == DepartmentsDetailsOfMembers.departmentIndex)