
# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import func, or_, and_

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.likesOnBoard import LikesOnBoard
from GradeServer.model.repliesOnBoard import RepliesOnBoard
from GradeServer.model.likesOnReplyOfBoard import LikesOnReplyOfBoard
from GradeServer.model.problems import Problems
from GradeServer.model.members import Members

from GradeServer.database import dao


'''
Join Course Name
'''
def join_course_name(articlesOnBoard, myCourses):
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
def select_article(articleIndex, isDeleted = ENUMResources.const.FALSE):   
      
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
           
'''
Article View Counting
'''
def update_view_reply_counting(articleIndex, VIEW_INCREASE = 1, REPLY_INCREASE = 0):
    dao.query(ArticlesOnBoard).\
            filter(ArticlesOnBoard.articleIndex == articleIndex).\
            update(dict(viewCount = ArticlesOnBoard.viewCount + VIEW_INCREASE,
                        replyCount = ArticlesOnBoard.replyCount + REPLY_INCREASE))
            
 
            
'''
 Board IsLike
'''
def select_article_is_like(boardLikerId, articleIndex):
    return dao.query(LikesOnBoard).\
               filter(LikesOnBoard.boardLikerId == boardLikerId,
                      LikesOnBoard.articleIndex == articleIndex)
               

'''
Board Article Like Counting
'''
def update_article_like_counting(articleIndex, LIKE_INCREASE = 1):
    dao.query(ArticlesOnBoard).\
        filter(ArticlesOnBoard.articleIndex == articleIndex).\
        update(dict(sumOfLikeCount = ArticlesOnBoard.sumOfLikeCount + LIKE_INCREASE))   
        
        
'''
Board Article isLike update
'''
def update_article_is_like(articleIndex, boardLikerId, isLikeCancelled = ENUMResources.const.FALSE):
    dao.query(LikesOnBoard).\
        filter(LikesOnBoard.articleIndex == articleIndex,
               LikesOnBoard.boardLikerId == boardLikerId).\
        update(dict(isLikeCancelled = isLikeCancelled))
             

'''
Board Article delete
'''
def update_article_delete(articleIndex, isDeleted = ENUMResources.const.TRUE): 
    dao.query(ArticlesOnBoard).\
        filter(ArticlesOnBoard.articleIndex == articleIndex).\
        update(dict(isDeleted = isDeleted))  
        
                    
'''
Replies on Board
'''
def select_replies_on_board(articleIndex, isDeleted = ENUMResources.const.FALSE):
    return dao.query(RepliesOnBoard).\
               filter(RepliesOnBoard.articleIndex == articleIndex,
                      RepliesOnBoard.isDeleted == ENUMResources.const.FALSE).\
               order_by(RepliesOnBoard.boardReplyIndex.desc())
               

'''
Replies on Board isLike
'''
def select_replies_on_board_is_like(articleIndex, boardReplyIndex, boardReplyLikerId):
    return dao.query(LikesOnReplyOfBoard).\
               filter(LikesOnReplyOfBoard.boardReplyLikerId == boardReplyLikerId,
                      LikesOnReplyOfBoard.articleIndex == articleIndex,
                      LikesOnReplyOfBoard.boardReplyIndex == boardReplyIndex)
               

'''
Replies on Board isLike
'''
def select_replies_on_board_like(repliesOnBoard, memberId):
    return dao.query(LikesOnReplyOfBoard).\
               join(repliesOnBoard,
                    and_(LikesOnReplyOfBoard.articleIndex == repliesOnBoard.c.articleIndex,
                         LikesOnReplyOfBoard.boardReplyIndex == repliesOnBoard.c.boardReplyIndex,
                         LikesOnReplyOfBoard.boardReplyLikerId == memberId)).\
               order_by(LikesOnReplyOfBoard.boardReplyIndex.desc())
               

'''
Repllies on Board Like Counting
'''
def update_replies_on_board_like_counting(articleIndex, boardReplyIndex, LIKE_INCREASE = 1):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.articleIndex == articleIndex,
               RepliesOnBoard.boardReplyIndex == boardReplyIndex).\
        update(dict(sumOfLikeCount = RepliesOnBoard.sumOfLikeCount + LIKE_INCREASE))  
        
'''
REplies on Board is LIke
'''
def update_replies_on_board_is_like(boardReplyIndex, boardReplyLikerId, isLikeCancelled = ENUMResources.const.FALSE):
    dao.query(LikesOnReplyOfBoard).\
        filter(LikesOnReplyOfBoard.boardReplyIndex == boardReplyIndex,
               LikesOnReplyOfBoard.boardReplyLikerId == boardReplyLikerId).\
        update(dict(isLikeCancelled = isLikeCancelled))


'''
Replies on Board Update
'''
def update_replies_on_board_modify(articleIndex, boardReplyIndex, boardReplyContent):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.articleIndex == articleIndex,
               RepliesOnBoard.boardReplyIndex == boardReplyIndex).\
        update(dict(boardReplyContent = boardReplyContent,
                    boardRepliedDate = datetime.now()))
        
        
'''
Repllies on Board delete
'''
def update_replies_on_board_delete(articleIndex, boardReplyIndex, isDelete = ENUMResources.const.TRUE):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.articleIndex == articleIndex,
               RepliesOnBoard.boardReplyIndex == boardReplyIndex).\
        update(dict(isDelete = isDelete)) 
