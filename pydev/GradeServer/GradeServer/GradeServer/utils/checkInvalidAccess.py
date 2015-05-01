# -*- coding: utf-8 -*-

from flask import request
from functools import wraps

from GradeServer.utils.utilMessages import unknown_error, get_message

def check_invalid_access(f):
    """
    Check invalid access through URL 
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # moved from URL, error will occur
            if not request.referrer:
                return unknown_error(get_message('invalidAccess'))
            
            return f(*args, **kwargs)

        except Exception:            
            return unknown_error ()

    return decorated_function