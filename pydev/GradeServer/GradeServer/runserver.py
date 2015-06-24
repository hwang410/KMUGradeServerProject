# -*- coding: utf-8 -*-
"""
    runserver
    ~~~~~~~~~

    Tornado Test

    :copyright: (c) 2015 by KookminUniv
    :license: MIT LICENSE 1.0, see license for more details.
"""

import sys

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from GradeServer import create_app

reload(sys).setdefaultencoding('utf-8')

application = create_app()

if __name__ == '__main__':
    '''jenkins test'''
    print 'running...'
    http_server = HTTPServer (WSGIContainer (application))
    http_server.bind(80)
    http_server.start(6)
    IOLoop.instance().start ()
    
