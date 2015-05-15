
# -*- coding: utf-8 -*-

from flask import session
from datetime import datetime
from sqlalchemy import or_, and_

from GradeServer.utils.utilQuery import select_accept_courses, select_current_courses
from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.otherResources import OtherResources

from GradeServer.utils.filterFindParameter import FilterFindParameter
from GradeServer.utils.memberCourseProblemParameter import MemberCourseProblemParameter
from GradeServer.utils.articleParameter import ArticleParameter
from GradeServer.utils.replyParameter import ReplyParameter

from GradeServer.utils.utilPaging import get_page_record

from GradeServer.model.members import Members
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
def select_article(articleParameter = ArticleParameter(), isDeleted = ENUMResources().const.FALSE):   
      
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.articleIndex == articleParameter.articleIndex,
                      ArticlesOnBoard.isDeleted == isDeleted)
               
                              
'''
Board Notice Classification
'''
def select_sorted_articles(articlesOnBoard, isNotice = ENUMResources().const.FALSE, filterFindParameter = FilterFindParameter()):
    articlesOnBoard = dao.query(articlesOnBoard).\
                          filter(articlesOnBoard.c.isNotice == isNotice,
                                 (or_(articlesOnBoard.c.courseName == None,
                                      articlesOnBoard.c.courseName != None) if isNotice == ENUMResources().const.TRUE
                                  else articlesOnBoard.c.courseName != None)).\
                          subquery()
    # Filter Case
    if filterFindParameter\
       and filterFindParameter.filterCondition: 
        articlesOnBoard = search_articles(articlesOnBoard,
                                          filterFindParameter).subquery()
        
    return dao.query(articlesOnBoard).\
               order_by(articlesOnBoard.c.articleIndex.desc())
'''
게시판 검색
'''
def search_articles(articlesOnBoard, filterFindParameter = FilterFindParameter()):
    # condition은 All, Id, Title&Content로 나누어서 검새
    if filterFindParameter.filterCondition == '모두': # Filters[0] is '모두'
        articlesOnBoard = dao.query(articlesOnBoard).\
                             filter(or_(articlesOnBoard.c.writerId.like('%' + filterFindParameter.keyWord + '%'), 
                                        articlesOnBoard.c.title.like('%' + filterFindParameter.keyWord + '%'),
                                        articlesOnBoard.c.content.like('%' + filterFindParameter.keyWord + '%')))
    elif filterFindParameter.filterCondition == '작성자': # Filters[1] is '작성자'
        articlesOnBoard = dao.query(articlesOnBoard).\
                              filter(articlesOnBoard.c.writerId.like('%' + filterFindParameter.keyWord + '%'))
    else: # Filters[2] is '제목&내용'
        articlesOnBoard = dao.query(articlesOnBoard).\
                              filter(or_(articlesOnBoard.c.title.like('% '+ filterFindParameter.keyWord + '%'), 
                                         articlesOnBoard.c.content.like('%' + filterFindParameter.keyWord + '%')))

    return articlesOnBoard
                       


'''
Article View Counting
'''
def update_view_reply_counting(articleParameter = ArticleParameter(), VIEW_INCREASE = 1, REPLY_INCREASE = 0):
    dao.query(ArticlesOnBoard).\
            filter(ArticlesOnBoard.articleIndex == articleParameter.articleIndex).\
            update(dict(viewCount = ArticlesOnBoard.viewCount + VIEW_INCREASE,
                        replyCount = ArticlesOnBoard.replyCount + REPLY_INCREASE))
            
 
            
'''
 Board IsLike
'''
def select_article_is_like(articleParameter = ArticleParameter()):
    return dao.query(LikesOnBoard).\
               filter(LikesOnBoard.articleIndex == articleParameter.articleIndex,
                      LikesOnBoard.boardLikerId == articleParameter.boardLikerId)
               

'''
Board Article Like Counting
'''
def update_article_like_counting(articleParameter = ArticleParameter(), LIKE_INCREASE = 1):
    dao.query(ArticlesOnBoard).\
        filter(ArticlesOnBoard.articleIndex == articleParameter.articleIndex).\
        update(dict(sumOfLikeCount = ArticlesOnBoard.sumOfLikeCount + LIKE_INCREASE))   
        
        
'''
Board Article isLike update
'''
def update_article_is_like(articleParameter = ArticleParameter(), isLikeCancelled = ENUMResources().const.FALSE):
    dao.query(LikesOnBoard).\
        filter(LikesOnBoard.articleIndex == articleParameter.articleIndex,
               LikesOnBoard.boardLikerId == articleParameter.boardLikerId).\
        update(dict(isLikeCancelled = isLikeCancelled))
             

'''
Board Article delete
'''
def update_article_delete(articleParameter = ArticleParameter(), isDeleted = ENUMResources().const.TRUE): 
    dao.query(ArticlesOnBoard).\
        filter(ArticlesOnBoard.articleIndex == articleParameter.articleIndex).\
        update(dict(isDeleted = isDeleted))  
        
                    
'''
Replies on Board
'''
def select_replies_on_board(articleParameter = ArticleParameter(), isDeleted = ENUMResources().const.FALSE):
    return dao.query(RepliesOnBoard).\
               filter(RepliesOnBoard.articleIndex == articleParameter.articleIndex,
                      RepliesOnBoard.isDeleted == ENUMResources().const.FALSE).\
               order_by(RepliesOnBoard.boardReplyIndex.desc())
               

'''
Replies on Board isLike
'''
def select_replies_on_board_is_like(replyParameter = ReplyParameter()):
    return dao.query(LikesOnReplyOfBoard).\
               filter(LikesOnReplyOfBoard.boardReplyLikerId == replyParameter.boardReplyLikerId,
                      LikesOnReplyOfBoard.boardReplyIndex == replyParameter.boardReplyIndex)
               

'''
Replies on Board isLike
'''
def select_replies_on_board_like(repliesOnBoard, memberCourseProblemParameter = MemberCourseProblemParameter()):
    return dao.query(LikesOnReplyOfBoard).\
               join(repliesOnBoard,
                    and_(LikesOnReplyOfBoard.boardReplyIndex == repliesOnBoard.c.boardReplyIndex,
                         LikesOnReplyOfBoard.boardReplyLikerId == memberCourseProblemParameter.memberId)).\
               order_by(LikesOnReplyOfBoard.boardReplyIndex.desc())
               

'''
Repllies on Board Like Counting
'''
def update_replies_on_board_like_counting(replyParameter = ReplyParameter(), LIKE_INCREASE = 1):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.boardReplyIndex == replyParameter.boardReplyIndex).\
        update(dict(sumOfLikeCount = RepliesOnBoard.sumOfLikeCount + LIKE_INCREASE))  
        
'''
REplies on Board is LIke
'''
def update_replies_on_board_is_like(replyParameter = ReplyParameter(), isLikeCancelled = ENUMResources().const.FALSE):
    dao.query(LikesOnReplyOfBoard).\
        filter(LikesOnReplyOfBoard.boardReplyIndex == replyParameter.boardReplyIndex,
               LikesOnReplyOfBoard.boardReplyLikerId == replyParameter.boardReplyLikerId).\
        update(dict(isLikeCancelled = isLikeCancelled))


'''
Replies on Board Update
'''
def update_replies_on_board_modify(replyParameter = ReplyParameter()):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.boardReplyIndex == replyParameter.boardReplyIndex).\
        update(dict(boardReplyContent = replyParameter.boardReplyContent,
                    boardRepliedDate = datetime.now()))
        
        
'''
Repllies on Board delete
'''
def update_replies_on_board_delete(replyParameter = ReplyParameter(), isDeleted = ENUMResources().const.TRUE):
    dao.query(RepliesOnBoard).\
        filter(RepliesOnBoard.boardReplyIndex == replyParameter.boardReplyIndex).\
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
                # 서버 공지만
        myCourses = select_accept_courses().subquery()
        try:
            serverAdministratorId = dao.query(Members.memberId).\
                                        filter(Members.authority == SETResources().const.SERVER_ADMINISTRATOR).\
                                        first().\
                                        memberId
        except:
            serverAdministratorId = None
            
        # TabActive Course or All Articles
        # get course or All Articles 
        articlesOnBoard = join_courses_names(select_server_notice(serverAdministratorId,
                                                                  isNotice = ENUMResources().const.TRUE,
                                                                  isDeleted = ENUMResources().const.FALSE).subquery(),
                                             myCourses).subquery()
    try:
                # 과목 공지글
        # Get ServerAdministrator is All, CourseAdministrators, Users is server and course Notice
                # 서버 관리자는 모든 공지
                # 과목 관리자 및 유저는 담당 과목 공지
        articleNoticeRecords = get_page_record((select_sorted_articles(articlesOnBoard,
                                                                       isNotice = ENUMResources().const.TRUE)),
                                               pageNum = int(1),
                                               LIST = OtherResources().const.NOTICE_LIST).all()
    except Exception:
        articleNoticeRecords = []
       
    return articleNoticeRecords 


''' 
Ger SErverNotices
'''
def select_server_notice(serverAdministratorId, isNotice = ENUMResources().const.TRUE, isDeleted = ENUMResources().const.FALSE):
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.courseId == None,
                      ArticlesOnBoard.writerId == serverAdministratorId,
                      ArticlesOnBoard.isNotice == isNotice,
                      ArticlesOnBoard.isDeleted == isDeleted)        