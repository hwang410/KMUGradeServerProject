# -*- coding: utf-8 -*-
"""
    GradeSever.controller.signUp
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Page for signing up

    :author: seulgi choi
    :copyright: (c) 2015 by KookminUniv

"""
from werkzeug import generate_password_hash
from flask import request, redirect, url_for, render_template, flash
from datetime import datetime

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer
from sqlalchemy import and_

from GradeServer.resource.setResources import SETResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.languageResources import LanguageResources

from GradeServer.model.departmentsDetailsOfMembers import DepartmentsDetailsOfMembers
from GradeServer.model.colleges import Colleges
from GradeServer.model.departments import Departments
from GradeServer.model.departmentsOfColleges import DepartmentsOfColleges
from GradeServer.model.members import Members

from __builtin__ import False

    
'''
@@ Check form data from request.form

Returns True if form data exists
'''
def has_form(form_name):
    if not request.form[form_name]:
        return False
    return True

def insert_into_departmentDetailsOfMembers(memberId, collegeIndex, departmentIndex):
    departmentInformation = DepartmentsDetailsOfMembers(memberId = memberId,
                                                        collegeIndex = int(collegeIndex),
                                                        departmentIndex = int(departmentIndex))
    dao.add(departmentInformation)

    try:
        dao.commit()
    except:
        dao.rollback()
        return False
            
    return True

def insert_into_Members(memberId, password, memberName, authority, signedInDate, comment):
    '''
    @@ TODO
    
    Default authority is USER.
    So if you want to make an account for server administrator,
    you change the authority in database terminal.
    '''
    newMember = Members(memberId = memberId,
                        password = password,
                        memberName = memberName,
                        authority = authority,
                        signedInDate = signedInDate,
                        comment = comment)
    dao.add(newMember)
    try:
        dao.commit()
    except:
        dao.rollback()
        return False
    
    return True

def get_colleges():
    colleges = dao.query(Colleges).\
                         filter(Colleges.isAbolished == SETResources().const.FALSE).\
                         all()
    return colleges

def get_relation_between_col_and_dep():
    relation = (dao.query(DepartmentsOfColleges,
                          Colleges,
                          Departments).\
                    filter(and_(Colleges.isAbolished == SETResources().const.FALSE,
                                Departments.isAbolished == SETResources().const.FALSE)).\
                    join(Colleges,
                         Colleges.collegeIndex == DepartmentsOfColleges.collegeIndex).\
                    join(Departments,
                         Departments.departmentIndex == DepartmentsOfColleges.departmentIndex)).\
               all()
    return relation

from GradeServer.py3Des.pyDes import *
def initialize_tripleDes_class():
    tripleDes = triple_des(OtherResources().const.TRIPLE_DES_KEY,
                           mode = ECB,
                           IV = '\0\0\0\0\0\0\0\0',
                           pad = None,
                           padmode = PAD_PKCS5)
    return tripleDes

def has_duplicated_member(memberId):
    try:
        dao.query(Members).\
            filter(Members.memberId == memberId).\
            first().\
            memberId
    except:
        return False
    
    return True
                                       
@GradeServer.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
    try:
        colleges = get_colleges()
        
    except:
        error = 'Error has been occurred while searching colleges. Please refresh the page.'
        return render_template('sign_up.html',
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               colleges = '',
                               departments = '',
                               error = error)
        
    try:
        departments = get_relation_between_col_and_dep()
        
    except:
        error = 'Error has been occurred while searching departments. Please refresh the page.'
        return render_template('sign_up.html',
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               LanguageResources = LanguageResources,
                               colleges = colleges,
                               departments = '',
                               error = error)
        
    error = None
    if request.method == 'POST':
        memberId = ''
        password = ''
        name = ''

        if not has_form('member_id') or\
           not has_form('password') or\
           not has_form('member_name'):
            error = 'Fill the necessary form'
            return render_template('sign_up.html',
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
                                   LanguageResources = LanguageResources,
                                   colleges = colleges,
                                   departments = departments,
                                   error = error)
            
        else:
            try:
                '''
                @@ check ID duplication
                
                If there's no same memberId in Member table,
                it will occur except procedure.
                So it can keep doing signing process.
                '''
                memberId = request.form['member_id']

                if not has_duplicated_member(memberId):
                    password = request.form['password']
                    name = request.form['member_name']
                    comment = request.form['comment'] if request.form['comment'] else ''
                                   
                    # encrypt password and transfer for insertion into DB
                    tripleDes = initialize_tripleDes_class()
                    password = generate_password_hash(tripleDes.encrypt(str(password)))

                    if not insert_into_Members(memberId, password, name, 'USER', datetime.now(), comment):
                        error = 'Error has been occurred while adding new user to DB'
                        return render_template('sign_up.html',
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               LanguageResources = LanguageResources,
                                               colleges = colleges,
                                               departments = departments,
                                               error = error)

                    college = request.form['college'].split()[0] if request.form['college'] else ''
                    department = request.form['department'].split()[0] if request.form['department'] else ''

                    if college and department:
                        if not insert_into_departmentDetailsOfMembers(memberId, college, department):
                            error = 'Error has been occurred while adding user's department information to DB'
                            return render_template("sign_up.html",
                                                   SETResources = SETResources,
                                                   SessionResources = SessionResources,
                                                   LanguageResources = LanguageResources,
                                                   colleges = colleges,
                                                   departments = departments,
                                                   error = error)

                    from GradeServer.resource.routeResources import RouteResources
                    return redirect(url_for(RouteResources().const.SIGN_IN, rdr=''))
                
                else:
                    error = 'Your ID is already exist'
                    return render_template('sign_up.html',
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           LanguageResources = LanguageResources,
                                           colleges = colleges,
                                           departments = departments,
                                           error = error)
                    
            except:
                error = 'Error has been occurred while adding new user'
                return render_template("sign_up.html",
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       LanguageResources = LanguageResources,
                                       colleges = colleges,
                                       departments = departments,
                                       error = error)
                    
    return render_template('/sign_up.html',
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           LanguageResources = LanguageResources,
                           colleges = colleges,
                           departments = departments,
                           error = error)
