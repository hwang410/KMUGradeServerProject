# -*- coding: utf-8 -*-
"""
    GradeServer.model
    ~~~~~~~~~~~~~~

    GradeServer 패키지 초기화 모듈. 
    GradeServer에 대한 flask 어플리케이션을 생성함.
    config, blueprint, session, DB연결 등을 초기화함.

    :copyright: (c) 2015 kookminUniv
"""

import os
from flask import Flask, render_template, request, url_for

def create_app(config_filepath ="resource/config.cfg"):
    app = Flask(__name__)
    #app.config.from_object(__name__)
    #app.config.from_envvar('GRADE_SETTINGS', silent=True)
    
    # 기본 설정은 GradeServer_Config 객체에 정의되있고 운영 환경 또는 기본 설정을 변경을 하려면
    # 실행 환경변수인 GradeServer_SETTINGS에 변경할 설정을 담고 있는 파일 경로를 설정 
    from GradeServer.GradeServer_config import GradeServerConfig
    app.config.from_object(GradeServerConfig)
    app.config.from_pyfile(config_filepath, silent=True)
    
    # SessionInterface 설정.
    from GradeServer.cache_session import RedisCacheSessionInterface
    app.session_interface = RedisCacheSessionInterface()
    
    # 데이터베이스 처리 
    from GradeServer.database import DBManager
    DBManager.init(app.config['DB_URL'], eval(app.config['DB_LOG_FLAG']))    
    DBManager.init_db()
    
        # 뷰 함수 모듈은 어플리케이션 객체 생성하고 블루프린트 등록전에 
        # 뷰 함수가 있는 모듈을 임포트해야 해당 뷰 함수들을 인식할 수 있음
    from GradeServer.controller import *
    from GradeServer.GradeServer_blueprint import GradeServer
    app.register_blueprint(GradeServer)
     
    return app