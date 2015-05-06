# -*- coding: utf-8 -*-
"""
    GradeServer.DB
    ~~~~~~~~~~~~~~

    GradeServer 패키지 초기화 모듈. 
    GradeServer에 대한 flask 어플리케이션을 생성함.
    config, blueprint, session, DB연결 등을 초기화함.

    :copyright: (c) 2015 kookminUniv
"""

def DatabaseInit():
    # 데이터베이스 처리 
    from DBManager import DBManager
    DBManager.init("mysql+mysqlconnector://root:dkfrhflwma@192.168.0.8/GradeServer_DB", False)    
    DBManager.init_db()
    print 'test message'
