
# -*- coding: utf-8 -*-

from sqlalchemy import func, or_

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.model.problems import Problems
from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.members import Members

'''
Join Course Name
'''
def join_course_name(articlesOnBoard, myCourses):
    print dao.query(myCourses).first().courseName, dao.query(myCourses).first().courseId
    return dao.query(articlesOnBoard,
                     myCourses.c.courseName).\
               outerjoin(myCourses,
                         articlesOnBoard.c.courseId == myCourses.c.courseId)
               
'''
Board Articles
'''
def select_articles(activeTabCourseId, isDeleted = ENUMResources.const.FALSE):
    
    # activate Tab Select
    if activeTabCourseId == OtherResources.const.ALL:
        return dao.query(ArticlesOnBoard).\
                   filter(ArticlesOnBoard.isDeleted == isDeleted)
    else:
        return dao.query(ArticlesOnBoard).\
                   filter(ArticlesOnBoard.isDeleted == isDeleted,
                          or_(ArticlesOnBoard.courseId == activeTabCourseId,
                              ArticlesOnBoard.courseId == None))
 
 
'''
Board Article
'''
def select_article(articleIndex, isDeleted):   
      
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.articleIndex == articleIndex,
                      ArticlesOnBoard.isDeleted == isDeleted)
               
                              
'''
Board Notice Classification
'''
def select_sorted_articles(articlesOnBoard, isNotice = ENUMResources.const.FALSE):
    return dao.query(articlesOnBoard).\
           filter(articlesOnBoard.c.isNotice == isNotice,
                  (or_(articlesOnBoard.c.courseName == None,
                       articlesOnBoard.c.courseName != None) if isNotice == ENUMResources.const.TRUE
                   else articlesOnBoard.c.courseName != None)).\
           order_by(articlesOnBoard.c.articleIndex.desc())
