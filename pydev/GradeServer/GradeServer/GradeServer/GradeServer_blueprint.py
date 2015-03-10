# -*- coding: utf-8 -*-

from flask import Blueprint
#from GradeServer_logger import Log

GradeServer = Blueprint('GradeServer', __name__, template_folder='../templates', static_folder='../static')

#Log.info('static folder : %s' % GradeServer.static_folder)
#Log.info('template folder : %s' % GradeServer.template_folder)