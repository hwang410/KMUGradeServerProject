# -*- coding: utf-8 -*-

from flask import session, request, current_app, redirect, url_for
from functools import wraps

from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.sessionResources import SessionResources

def login_required(f):
    """현재 사용자가 로그인 상태인지 확인하는 데코레이터
    로그인 상태에서 접근 가능한 함수에 적용함
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session_key = \
                request.cookies.get(
                    current_app.config['SESSION_COOKIE_NAME'])

            if not (session.sid == session_key and session.__contains__(SessionResources().const.MEMBER_ID)):
                session.clear()
             
                return redirect(url_for(RouteResources().const.SIGN_IN))
            
            return f(*args, **kwargs)

        except Exception:
            from GradeServer.utils.utilMessages import unknown_error
            
            return unknown_error ()

    return decorated_function