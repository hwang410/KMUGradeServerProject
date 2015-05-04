
# -*- coding: utf-8 -*-

from flask import session
from datetime import datetime
from sqlalchemy import or_, and_

from GradeServer.utils.utilQuery import select_accept_courses, select_current_courses
from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.sessionResources import SessionResources
from GradeServer.resource.otherResources import OtherResources

from GradeServer.utils.utilPaging import get_page_record

from GradeServer.model.members import Members
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.registrations import Registrations
from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.likesOnBoard import LikesOnBoard
from GradeServer.model.repliesOnBoard import RepliesOnBoard
from GradeServer.model.likesOnReplyOfBoard import LikesOnReplyOfBoard

from GradeServer.database import dao


'''
Join Course Name
'''
def join_courses_names(articlesOnBoard, myCourses):
    return dao.query(articlesOnBoard,
                     myCourses.c.courseName).\
               outerjoin(myCourses,
                         articlesOnBoard.c.courseId == myCourses.c.courseId)
               
'''
Board Articles
'''
def select_articles(activeTabCourseId, isDeleted = ENUMResources().const.FALSE):
    
    # activate Tab Select
    if activeTabCourseId == OtherResources().const.ALL:
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
def select_article(articleIndex, isDeleted = ENUMResources().const.FALSE):   
      
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.articleIndex == articleIndex,
                      ArticlesOnBoard.isDeleted == isDeleted)
               
                              
'''
Board Notice Classification
'''
def select_sorted_articles(articlesOnBoard, isNotice = ENUMResources().const.FALSE, filterCondition = None, keyWord = None):
    articlesOnBoard = dao.query(articlesOnBoard).\
                          filter(articlesOnBoard.c.isNotice == isNotice,
                                 (or_(articlesOnBoard.c.courseName == None,
                                      articlesOnBoard.c.courseName != None) if isNotice == ENUMResources().const.TRUE
                                  else articlesOnBoard.c.courseName != None)).\
                          subquery()
    # Filter Case
    if filterCondition: 
        articlesOnBoard = search_articles(articlesOnBoard,
                                          filterCondition = filterCondition,
                                          keyWord = keyWord).subquery()
        
    return dao.query(articlesOnBoard).\
               order_by(articlesOnBoard.c.articleIndex.desc())
'''
게시판 검색
'''
def search_articles(articlesOnBoard, filterCondition, keyWord =''):
    # condition은 All, Id, Title&Content로 나누어서 검새
    if filterCondition == '모두': # Filters[0] is '모두'
        articlesOnBoard = dao.query(articlesOnBoard).\
                             filter(or_(articlesOnBoard.c.writerId.like('%' + keyWord + '%'), 
                                        articlesOnBoard.c.title.like('%' + keyWord + '%'),
                                        articlesOnBoard.c.content.like('%' + keyWord + '%')))
    elif filterCondition == '작성자': # Filters[1] is '작성자'
        articlesOnBoard = dao.query(articlesOnBoard).\
                              filter(articlesOnBoard.c.writerId.like('%' + keyWord + '%'))
    else: # Filters[2] is '제목&내용'
        articlesOnBoard = dao.query(articlesOnBoard).\
                              filter(or_(articlesOnBoard.c.title.like('% '+ keyWord + '%'), 
                                         articlesOnBoard.c.content.like('%' + keyWord + '%')))

    return articlesOnBoard
                       


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
def select_article_is_like(articleIndex, boardLikerId):
    return dao.query(LikesOnBoard).\
               filter(LikesOnBoard.articleIndex == articleIndex,
                      LikesOnBoard.boardLikerId == boardLikerId)
               

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
def update_article_is_like(articleIndex, boardLikerId, isLikeCancelled = ENUMResources().const.FALSE):
    dao.query(LikesOnBoard).\
        filter(LikesOnBoard.articleIndex == articleIndex,
               LikesOnBoard.boardLikerId == boardLikerId).\
        update(dict(isLikeCancelled = isLikeCancelled))
             

'''
Board Article delete
'''
def update_article_delete(articleIndex, isDeleted = ENUMResources().const.TRUE): 
    dao.query(ArticlesOnBoard).\
        filter(ArticlesOnBoard.articleIndex == articleIndex).\
        update(dict(isDeleted = isDeleted))  
        
                    
'''
Replies on Board
'''
def select_replies_on_board(articleIndex, isDeleted = ENUMResources().const.FALSE):
    return dao.query(RepliesOnBoard).\
               filter(RepliesOnBoard.articleIndex == articleIndex,
                      RepliesOnBoard.isDeleted == ENUMResources().const.FALSE).\
               order_by(RepliesOnBoard.boardReplyIndex.desc())
               

'''
Replies on Board isLike
'''
def select_replies_on_board_is_like(boardReplyIndex, boardReplyLikerId):
    return dao.query(LikesOnReplyOfBoard).\
               filter(LikesOnReplyOfBoard.boardReplyLikerId == boardReplyLikerId,
                      LikesOnReplyOfBoard.boardReplyIndex == boardReplyIndex)
               

'''
Replies on Board isLike
'''
def select_replies_on_board_like(repliesOnBoard, memberId):
    return dao.query(LikesOnReplyOfBoard).\
               join(repliesOnBoard,
                    and_(LikesOnReplyOfBoard.boardReplyIndex == repliesOnBoard.c.boardReplyIndex,
                         LikesOnReplyOfBoard.boardReplyLikerId == memberId)).\
               order_by(LikesOnReplyOfBoard.boardReplyIndex.desc())
               

'''
Repllies on Board Like Counting
'''
def update_replies_on_board_like_counting(boardReplyIndex, LIKE_INCREASE = 1):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.boardReplyIndex == boardReplyIndex).\
        update(dict(sumOfLikeCount = RepliesOnBoard.sumOfLikeCount + LIKE_INCREASE))  
        
'''
REplies on Board is LIke
'''
def update_replies_on_board_is_like(boardReplyIndex, boardReplyLikerId, isLikeCancelled = ENUMResources().const.FALSE):
    dao.query(LikesOnReplyOfBoard).\
        filter(LikesOnReplyOfBoard.boardReplyIndex == boardReplyIndex,
               LikesOnReplyOfBoard.boardReplyLikerId == boardReplyLikerId).\
        update(dict(isLikeCancelled = isLikeCancelled))


'''
Replies on Board Update
'''
def update_replies_on_board_modify(boardReplyIndex, boardReplyContent):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.boardReplyIndex == boardReplyIndex).\
        update(dict(boardReplyContent = boardReplyContent,
                    boardRepliedDate = datetime.now()))
        
        
'''
Repllies on Board delete
'''
def update_replies_on_board_delete(boardReplyIndex, isDeleted = ENUMResources().const.TRUE):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.boardReplyIndex == boardReplyIndex).\
        update(dict(isDeleted = isDeleted)) 



'''
 DB Select Notices
 권한 별로 공지 가져오기
'''
def select_notices():
    # Notices Layer
    
        # 로그인 상태
    if session:
                # 허용 과목 리스트
        myCourses = select_current_courses(select_accept_courses().subquery()).subquery()
        
        # TabActive Course or All Articles
        # get course or All Articles 
        articlesOnBoard = join_courses_names(# get TabActive Articles
                                             select_articles(OtherResources().const.ALL,
                                                             isDeleted = ENUMResources().const.FALSE).subquery(),
                                             myCourses).subquery()
    # Not Login     
    else:  
        print "SFSDFEWR"
                # 서버 공지만
        myCourses = []
        try:
            serverAdministratorId = dao.query(Members.memberId).\
                                        filter(Members.authority == SETResources().const.SERVER_ADMINISTRATOR).\
                                        first().\
                                        memberId
        except:
            print "AAAAAAAAAAAAAA"
            serverAdministratorId = None
            
        # TabActive Course or All Articles
        # get course or All Articles 
        '''articlesOnBoard = join_courses_names(select_server_notice(serverAdministratorId).subquery(),
                                             myCourses).subquery()'''
        #print len(dao.query(articlesOnBoard).all())
    try:
        print "CGFDSFSDF"
                # 과목 공지글
        # Get ServerAdministrator is All, CourseAdministrators, Users is server and course Notice
                # 서버 관리자는 모든 공지
                # 과목 관리자 및 유저는 담당 과목 공지
        articleNoticeRecords = get_page_record((select_sorted_articles(articlesOnBoard,
                                                                       isNotice = ENUMResources().const.TRUE)),
                                               pageNum = int(1),
                                               LIST = OtherResources().const.NOTICE_LIST).all()
    except Exception:
        print "AAAAA"
        articleNoticeRecords = []
       
    return articleNoticeRecords 


''' 
Ger SErverNotices
'''
def select_server_notice(serverAdministratorId):
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.writerId == serverAdministratorId,
                      ArticlesOnBoard.isNotice == ENUMResources().const.TRUE,
                      ArticlesOnBoard.isDeleted == ENUMResources().const.FALSE)        