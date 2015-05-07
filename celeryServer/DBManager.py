# -*- coding: utf-8 -*-
"""
    photolog.database
    ~~~~~~~~~~~~~~~~~

    DB 연결 및 쿼리 사용을 위한 공통 모듈.

    :copyright: (c) 2013 by 4mba.
    :license: MIT LICENSE 2.0, see license for more details.
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from DB import Base


engine = create_engine("mysql+mysqlconnector://root:dkfrhflwma@192.168.0.8/GradeServer_DB",
                      convert_unicode = True, pool_recycle = 3600, pool_size=10) #echo =db_log_flag)

db_session = scoped_session(sessionmaker(
                                         autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.metadata.create_all(bind=engine)