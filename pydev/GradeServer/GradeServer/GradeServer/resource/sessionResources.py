

class SessionResources(object):
    """SESSION Resource Static Class"""
    
    from GradeServer.resource import const

    # session
    const.MEMBER_ID = 'memberId'
    const.AUTHORITY = 'authority'
    const.LAST_ACCESS_DATE = 'lastAccessDate'
    const.OWN_CURRENT_COURSES = 'ownCurrentCourses'
    const.OWN_PAST_COURSES = 'ownPastCourses'