

class RouteResources(object):
    """ROUTE Resource Static Class"""
    
    from GradeServer.resource import const

    # Login routes
    const.SIGN_IN = '.sign_in'
    
    # Board routes
    const.BOARD = '.board'
    const.READ = '.read'

    # Team routes
    const.TEAM = '.team'
    
    # User routes
    const.EDIT_PERSONAL = '.edit_personal'
    const.USER_HISTORY = '.user_history'