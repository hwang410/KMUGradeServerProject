# -*- coding: utf-8 -*-
"""
    GradeSever.controller.login
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    로그인 확인 데코레이터와 로그인 처리 모듈.

    :copyright: (c) 2015 by KookminUniv

"""
from werkzeug import generate_password_hash
from flask import request, redirect, url_for, render_template, flash
from datetime import datetime

from GradeServer.database import dao
from GradeServer.GradeServer_blueprint import GradeServer

'''
@@ Check form data from request.form

Returns True if form data exists
'''
def has_form(form_name):
    if not request.form[form_name]:
        return False
    return True

@GradeServer.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():        
    '''
    @@ import for main page 
    '''
    from GradeServer.resource.setResources import SETResources
    from GradeServer.resource.sessionResources import SessionResources
    
    error = None
    if request.method == 'POST':
        memberId = ''
        password = ''
        name = ''

        if not has_form('member_id') or\
           not has_form('password') or\
           not has_form('member_name'):
            error = 'Fill the necessary form'
            return render_template("sign_up.html",
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
                                   error = error)
            
        else:
            try:
                '''
                @@ import for insertion new member to DB
                '''
                from GradeServer.model.members import Members
                from GradeServer.resource.otherResources import OtherResources
                
                '''
                @@ check ID duplication
                
                If there's no same memberId in Member table,
                it will occur except procedure.
                So it can keep doing signing process.
                '''
                memberId = request.form['member_id']
                
                try:
                    checkIfExist = dao.query(Members).\
                                       filter(Members.memberId == memberId).\
                                       first().\
                                       memberId
                
                except:
                    password = request.form['password']
                    name = request.form['member_name']
                    comment = request.form['comment'] if not request.form['comment'] else ''
                    
                    '''
                    @@ import for encryption password
                    '''
                    from GradeServer.py3Des.pyDes import *
                    
                    '''
                    @@ Class initialization
                    '''
                    tripleDes = triple_des(OtherResources().const.TRIPLE_DES_KEY,
                                           mode = ECB,
                                           IV = "\0\0\0\0\0\0\0\0",
                                           pad = None,
                                           padmode = PAD_PKCS5)
                    
                    # encrypt password and transfer for insertion into DB
                    password = generate_password_hash(tripleDes.encrypt(str(password)))
                    
                    try:
                        '''
                        @@ IMPORTANT
                        !! change authority before real service !!
                        
                        It's for initial server administrator registration.
                        So, default authority is 'SERVER_ADMINISTRATOR'.
                        '''
                        newMember = Members(memberId = memberId,
                                            password = password,
                                            memberName = name,
                                            authority = 'SERVER_ADMINISTRATOR',
                                            signedInDate = datetime.now(),
                                            comment = comment)
                        dao.add(newMember)
                        dao.commit()
                    except:
                        error = 'Error has been occurred while adding new user to DB'
                        return render_template("sign_up.html",
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               error = error)
                       
                    from GradeServer.resource.routeResources import RouteResources
                    return redirect(url_for(RouteResources().const.SIGN_IN))
                
                if checkIfExist:
                    error = "Your ID is already exist"
                    return render_template("sign_up.html",
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           error = error)
                    
            except:
                error = 'Error has been occurred while adding new user'
                return render_template("sign_up.html",
                                       SETResources = SETResources,
                                       SessionResources = SessionResources,
                                       error = error)
                    
    return render_template('/sign_up.html',
                           SETResources = SETResources,
                           SessionResources = SessionResources,
                           error = error)