# -*- coding: utf-8 -*-
'''
    GradeSever.controller.board
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    로그인 확인 데코레이터와 로그인 처리 모듈.

   :copyright:(c) 2015 by KookminUniv

'''

import socket

from flask import render_template, request, session, redirect, url_for, flash
from datetime import datetime
from sqlalchemy import func, or_

from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilQuery import select_accept_courses, select_count

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.likesOnBoard import LikesOnBoard
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.repliesOnBoard import RepliesOnBoard
from GradeServer.model.likesOnReplyOfBoard import LikesOnReplyOfBoard
from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer 

@GradeServer.teardown_request
def close_db_session(exception = None):
    '''요청이 완료된 후에 db연결에 사용된 세션을 종료함'''
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))


'''
게시판을 과목별 혹은 전체 통합으로
보여주는 페이지
'''
@GradeServer.route('/board/<activeTabCourseId>/page<pageNum>', methods = ['GET', 'POST'])
@login_required
def board(activeTabCourseId, pageNum):    
    try:
        # 검색시 FilterCondition List
        Filters = ['모두', '작성자', '제목 및 내용']
        
        # get TabActive Articles
        articlesOnBoard = select_articles(activeTabCourseId,
                                          ENUMResources.const.FALSE).subquery()
                # 허용 과목 리스트
        myCourses = select_accept_courses().subquery()

        # join Course Name
        articlesOnBoard = join_course_name(articlesOnBoard, myCourses).subquery()
        # TabActive Course Articles
                # 과목 게시글
        try:
            articleSub = select_sorted_articles(articlesOnBoard,
                                                ENUMResources.const.FALSE)
            articleRecords = get_page_record(articleSub,
                                             int(pageNum)).all()
            count = select_count(articleSub.subquery().\
                                            c.\
                                            articleIndex).first().\
                                                          count
        except Exception:
            count = 0
            articleRecords = []
                # 과목 공지글    
        try:  
            articleNoticeRecords = get_page_record((select_sorted_articles(articlesOnBoard,
                                                                           ENUMResources.const.TRUE)),
                                                   int(1),
                                                   OtherResources.const.NOTICE_LIST).all()
        except Exception:
            articleNoticeRecords = []
        try:
            myCourses = dao.query(myCourses).all()
        except Exception:
            myCourses = []
        # myCourses Default Add ALL
        myCourses.insert(0, OtherResources.const.ALL)
       
        return render_template(HTMLResources.const.BOARD_HTML,
                               SETResources = SETResources,
                               articleRecords = articleRecords,
                               articleNoticeRecords =  articleNoticeRecords,
                               myCourses = myCourses,
                               pages = get_page_pointed(int(pageNum),
                                                        count),
                               Filters = Filters,
                               activeTabCourseId = activeTabCourseId) # classType, condition은 검색 할 때 필요한 변수    
        
    except Exception:
        return unknown_error()
                            

'''
Join Course Name
'''
def join_course_name(articlesOnBoard, myCourses):
    
    return dao.query(articlesOnBoard,
                     myCourses.c.courseName).\
               outerjoin(myCourses,
                         articlesOnBoard.c.courseId == myCourses.c.courseId)
               

'''
Board Article
'''
def select_article(articleIndex, isDeleted):   
      
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.articleIndex == articleIndex,
                      ArticlesOnBoard.isDeleted == isDeleted)
               
               
'''
Board Articles
'''
def select_articles(activeTabCourseId, isDeleted):
    
    # activate Tab Select
    if activeTabCourseId == OtherResources.const.ALL:
        return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.isDeleted == isDeleted)
    else:
        return  dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.isDeleted == isDeleted,
                      or_(ArticlesOnBoard.courseId == activeTabCourseId,
                          ArticlesOnBoard.courseId == None))
    

               
'''
Board Notice Classification
'''
def select_sorted_articles(articlesOnBoard, isNotice):
    
    return dao.query(articlesOnBoard).\
               filter(articlesOnBoard.c.isNotice == isNotice).\
               order_by(articlesOnBoard.c.articleIndex.desc())
 
 
'''
게시글을 눌렀을 때 
글 내용을 보여주는 페이지
'''
@GradeServer.route('/board/<articleIndex>', methods = ['GET', 'POST'])
@login_required
def read(articleIndex, error = None):
    ''' when you push a title of board content '''
    # Final 
    try:
        # 게시글 정보
        articlesOnBoard = select_article(articleIndex,
                                          ENUMResources.const.FALSE).subquery()
        try:
            articlesOnBoard = join_course_name(articlesOnBoard, 
                                               dao.query(RegisteredCourses).\
                                                   subquery()).first()
        except Exception:
            articlesOnBoard = []
            
        # 내가 게시글에 누른 좋아요 정보submissionCount
        try:
            isPostLiked = select_article_is_like(session[SessionResources.const.MEMBER_ID],
                                                 articleIndex).first().\
                                                               isLikeCancelled
        except Exception:
            isPostLiked = None
            
        # replies 정보
        try:
            commentRecords = dao.query(RepliesOnBoard).\
                           filter(RepliesOnBoard.isDeleted == ENUMResources.const.FALSE,
                                  RepliesOnBoard.articleIndex == articleIndex).\
                           order_by(RepliesOnBoard.boardReplyIndex.desc()).\
                           all()
        except Exception:
            commentRecords = []
            
        # 내가 게시글 리플에 누른 좋아요 정보
        try:
            boardReplyLikeCheckRecords = dao.query(LikesOnReplyOfBoard).\
                                      filter(LikesOnReplyOfBoard.articleIndex == articleIndex,
                                             LikesOnReplyOfBoard.boardReplyLikerId == session[SessionResources.const.MEMBER_ID],
                                             LikesOnReplyOfBoard.isLikeCancelled == ENUMResources.const.FALSE).\
                                      order_by(LikesOnReplyOfBoard.boardReplyIndex.desc()).\
                                      all()
        except Exception:
            boardReplyLikeCheckRecords = []
        # 나의 댓글 좋아요 여부 적용
        subIndex = 0
        isLikeds = []
        for i in range(0, len(commentRecords)):
            # 나의 댓글 좋아요 정보 비교
            isLikeds.append(dict(isLiked = ENUMResources.const.FALSE))
            for j in range(subIndex, len(boardReplyLikeCheckRecords)):
                if commentRecords[i].boardReplyIndex == boardReplyLikeCheckRecords[j].boardReplyIndex:
                    isLikeds[i]['isLiked'] = ENUMResources.const.TRUE
                    # 다음 시작 루프 인덱스 변경
                    subIndex = j
                    
                    break 
        # deleteCheck = dao.query(BoardReplyLike).filter_by(articleIndex=articleIndex).all()
    except Exception as e:
        Log.error(str(e))
        
    if request.method == 'GET':
        # 읽은 횟수 카운팅
        dao.query(ArticlesOnBoard).\
            filter(ArticlesOnBoard.articleIndex == articleIndex).\
            update(dict(viewCount = articlesOnBoard.viewCount + 1))
        # Commit Exception
        try:
            dao.commit()
            
            return render_template(HTMLResources.const.ARTICLE_READ_HTML,
                                   SETResources = SETResources,
                                   article = articlesOnBoard,
                                   commentRecords = commentRecords,
                                   isLikeds = isLikeds,
                                   isPostLiked = isPostLiked,
                                   error = error)
        except Exception:
            dao.rollback()
            
            return unknown_error()
    elif request.method == 'POST':
        # flash message Init
        flashMsg =None
        for form in request.form:
            
            # 게시글 좋아요
            if form == 'postLike':
                # 좋아요를 누른적 없을 때
                if not isPostLiked:
                    update_board_like_count(articleIndex,
                                            articlesOnBoard.sumOfLikeCount + 1)
                    dao.add(LikesOnBoard(articleIndex = articleIndex,
                                        boardLikerId = session[SessionResources.const.MEMBER_ID]))
                # 다시 좋아요 누를 때
                elif isPostLiked == ENUMResources.const.FALSE:
                    
                    update_board_like_count(articleIndex,
                                            articlesOnBoard.sumOfLikeCount + 1)
                    update_board_liker_cancelled (articleIndex,
                                                  session[SessionResources.const.MEMBER_ID],
                                                  ENUMResources.const.FALSE)
                # 좋아요 취소 할 때
                else:  # if it's already exist then change the value of 'pushedLike'
                    
                    update_board_like_count(articleIndex,
                                            articlesOnBoard.sumOfLikeCount -1)
                    update_board_liker_cancelled (articleIndex,
                                                  session[SessionResources.const.MEMBER_ID],
                                                  ENUMResources.const.FALSE)
                    
                # remove duplicated read count
                dao.query(ArticlesOnBoard).\
                    filter(ArticlesOnBoard.articleIndex == articleIndex).\
                    update(dict(viewCount = articlesOnBoard.viewCount - 1))
                
                break 
                # 댓글 달기
            elif form == 'boardCommentWrite':
                
                # 현재 게시물의 댓글중에 마지막 인덱스
                boardReplyIndex =dao.query(func.max(RepliesOnBoard.boardReplyIndex).label('boardReplyIndex')).\
                    filter_by(articleIndex =articleIndex).first().boardReplyIndex
                # 첫 댓글일 경우
                if not boardReplyIndex:
                    boardReplyIndex = 1
                else:
                    boardReplyIndex += 1
                
                # 새로운 댓글 정보
                newComment = RepliesOnBoard(boardReplyIndex = boardReplyIndex,
                                            articleIndex = articlesOnBoard.articleIndex,
                                            boardReplierId = session[SessionResources.const.MEMBER_ID],
                                            boardReplyContent = request.form['boardCommentWrite'],
                                            boardReplierIp = socket.gethostbyname(socket.gethostname()),
                                            boardRepliedDate = datetime.now())
                dao.add(newComment)
                # remove duplicated read count
                dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=articlesOnBoard.viewCount - 1, replyCount =articlesOnBoard.replyCount + 1))
                
                flashMsg =get_message('writtenComment')
                
                break 
            # 댓글 좋아요
            elif 'boardReplyLike' in form:  # the name starts with 'replyLike' and it has its unique number
                idIndex = len('boardReplyLike')
                # 해당 댓글의 좋아요 갯수
                sumOfLikeCount = dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[idIndex:])).first().sumOfLikeCount
                # 
                commentLikeCheck = dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[idIndex:]),
                                                                             boardReplyLikerId =session['memberId']).first()
                if not commentLikeCheck:  # initial pushing
                    dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[idIndex:])).update(dict(sumOfLikeCount=sumOfLikeCount + 1))
                    newLike = LikesOnReplyOfBoard(articleIndex=articleIndex, boardReplyIndex =int(form[idIndex:]), boardReplyLikerId =session['memberId'])
                    dao.add(newLike)
                else:
                    if commentLikeCheck.isLikeCancelled == 'Cancelled':
                        dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[idIndex:])).update(dict(sumOfLikeCount =sumOfLikeCount + 1))
                        dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[idIndex:]),
                                                                  boardReplyLikerId =session['memberId']).update(dict(isLikeCancelled ='Not-Cancelled'))
                    else:
                        dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[idIndex:]),
                                                                  boardReplyLikerId =session['memberId']).update(dict(isLikeCancelled ='Cancelled'))
                        dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[idIndex:])).update(dict(sumOfLikeCount=sumOfLikeCount - 1))
                # remove duplicated read count
                dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=articlesOnBoard.viewCount - 1))
                
                break 
            # 댓글 삭제   
            elif 'deleteBoardComment' in form:
                
                idIndex = len('deleteBoardComment')
                
                deleteCheck = dao.query(RepliesOnBoard.isDeleted).\
                                  filter(RepliesOnBoard.articleIndex == articleIndex,
                                         RepliesOnBoard.boardReplyIndex == form[idIndex:]).\
                                  first()
                
                # 삭제 시킬 경우
                if deleteCheck.isDeleted == 'Not-Deleted':
                    dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=form[idIndex:]).update(dict(isDeleted ='Deleted'))
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(replyCount=articlesOnBoard.replyCount - 1))
                    # remove duplicated read count
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=articlesOnBoard.viewCount - 1))
                    
                    flashMsg =get_message('deletedComment')
                    
                    break 
            # Commit Modify
            elif 'modifyConfirmBoardComment' in form:
                
                idIndex = len('modifyConfirmBoardComment')
                # remove duplicated read count
                dao.query(ArticlesOnBoard).\
                    filter(ArticlesOnBoard.articleIndex == articleIndex).\
                    update(dict(viewCount = articlesOnBoard.viewCount - 1))
                #update comment
                dao.query(RepliesOnBoard).\
                    filter(RepliesOnBoard.articleIndex == articleIndex,
                           RepliesOnBoard.boardReplyIndex == form[idIndex:]).\
                    update(dict(boardReplyContent = request.form['modifyConfirmBoardComment' + form[idIndex:]],
                                boardRepliedDate = datetime.now()))
               
                flashMsg =get_message('modifiedComment')
                
                break
            
            elif 'modifyBoardComment' in form:
               
                idIndex = len('modifyBoardComment')

                return render_template(HTMLResources.const.ARTICLE_READ_HTML,
                                       SETResources = SETResources,
                                       article = articlesOnBoard,
                                       commentRecords = commentRecords,
                                       boardReplyIndex = int(form[idIndex:]),
                                       isLikeds = isLikeds,
                                       isPostLiked = isPostLiked,
                                       error = error)
            # 게시물 삭제
            elif form == 'deletePost':
                deleteCheck = dao.query(ArticlesOnBoard.isDeleted).filter_by(articleIndex=articleIndex).first()
                if deleteCheck.isDeleted == 'Not-Deleted':
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(isDeleted ='Deleted'))
                    
                    # Commit Exception
                    try:
                        dao.commit()
                        flash(get_message('deletedPost'))
                    except Exception:
                        dao.rollback()
                        error = get_message('updateFailed')
                        
                    return redirect(url_for(RouteResources.const.BOARD,
                                            SETResources = SETResources,
                                            activeTabCourseId = OtherResources.const.ALL,
                                            pageNum = 1))
        
        # Commit Exception
        try:
            dao.commit()
            # if flash Message exist
            if flashMsg:
                flash(flashMsg)
        except Exception:
            dao.rollback()
            error = get_message('updateFailed')
            
        return redirect(url_for(RouteResources.const.ARTICLE_READ,
                                SETResources = SETResources,
                                articleIndex = articleIndex,
                                error = error))
    
    # Exception View    
    return redirect(url_for(RouteResources.const.BOARD,
                            SETResources = SETResources,
                            activeTabCourseId = OtherResources.const.ALL,
                            pageNum = 1))


'''
게시판에 글을 쓰는 페이지
'''
@GradeServer.route('/board/write/<articleIndex>', methods=['GET', 'POST'])
@login_required
def write(articleIndex, error =None):
    title, content =None, None
    try:
        # 수강  과목 정보
        try:
            myCourses = select_accept_courses().all()
        except Exception:
            myCourses = []
        
        # 수정 할 글 정보
        try:
            articlesOnBoard = select_article(articleIndex, ENUMResources.const.FALSE).subquery()
            articlesOnBoard = join_course_name(articlesOnBoard,
                                               dao.query(RegisteredCourses).\
                                                   subquery()).first()
        except Exception:
            articlesOnBoard =[]
        
        # 작성시 빈칸 검사
        if request.method == 'POST':
            if not request.form['title']:
                error ='제목' +get_message('fillData')
            elif not request.form['content']:
                # 타이틀 가져오기
                title =request.form['title']
                error ='내용' +get_message('fillData')
            elif len(request.form['title']) > 50:
                # 타이틀 가져오기
                title =request.form['title']
                # 내용 가져오기
                content =request.form['content']
                error = 'Title is too long. please write less than 50 letters'
            else:
                try:
                    # request.form['courseId']가 ex)2015100101 전산학 실습 일경우 중간의 공백을 기준으로 나눔
                    courseId = request.form['courseId'].split()[0]
                    if courseId == OtherResources.const.ALL:
                        courseId = None
                    isNotice = ENUMResources.const.TRUE
                    title = request.form['title']
                    content = request.form['content']
                    currentDate = datetime.now()
                    currentIP = socket.gethostbyname(socket.gethostname())
                    # 새로 작성
                    if not articlesOnBoard:
                        # Set isNotice
                        if SETResources.const.USER in session['authority']: 
                            isNotice = ENUMResources.const.FALSE
                        newPost = ArticlesOnBoard(problemId =problemId,
                                                  courseId = courseId,
                                                  writerId = session[SessionResources.const.MEMBER_ID],
                                                  isNotice = isNotice,
                                                  title = title,
                                                  content = content,
                                                  writtenDate = currentDate,
                                                  writerIp = currentIP)
                        dao.add(newPost)
                        # Commit Exception
                        try:
                            dao.commit()
                            flash(get_message('writtenPost'))
                        except Exception:
                            dao.rollback()
                            error =get_message('updateFailed')
                            
                        return redirect(url_for(RouteResources.const.BOARD,
                                                SETResources = SETResources,
                                                activeTabCourseId = OtherResources.const.ALL,
                                                pageNum = 1))
                    # 게시물 수정    
                    else:
                        articlesOnBoard = select_article(articleIndex,
                                                          ENUMResources.const.FALSE)
                        articlesOnBoard = articlesOnBoard.update(dict(courseId = courseId,
                                                                      title = title,
                                                                      content = content,
                                                                      writtenDate = currentDate,
                                                                      writerIp = currentIP))
                        
                        # Commit Exception
                        try:
                            dao.commit()
                            flash(get_message('modifiedPost'))
                        except Exception:
                            dao.rollback()
                            error =get_message('updateFailed')
                        # request.form['courseId']가 ex)2015100101 전산학 실습 일경우 
                        return redirect(url_for(RouteResources.const.ARTICLE_READ,
                                                SETResources = SETResources,
                                                courseName = request.form['courseId'].split()[1],
                                                articleIndex = articleIndex))
                
                except Exception:
                    error =get_message()
 
        return render_template(HTMLResources.const.ARTICLE_WRITE_HTML,
                               SETResources = SETResources,
                               myCourses = myCourses,
                               articlesOnBoard = articlesOnBoard,
                               title = title,
                               content = content,
                               error = error)
    except Exception:
        # Unknown Error
        return unknown_error()

'''
 Board IsLike
'''
def select_article_is_like(boardLikerId, articleIndex):
    
    return dao.query(LikesOnBoard).\
               filter(LikesOnBoard.boardLikerId == boardLikerId,
                      LikesOnBoard.articleIndex == articleIndex)
               
               
'''
  Board Like Count
'''
def update_board_like_count(articleIndex, count):
    dao.query(ArticlesOnBoard).\
        filter(ArticlesOnBoard.articleIndex == articleIndex).\
        update(dict(sumOfLikeCount = count))   
               
'''
Board LIker Cancelled
'''
def update_board_liker_cancelled(articleIndex, likerId, isLikeCancelled):
    dao.query(LikesOnBoard).\
        filter(LikesOnBoard.articleIndex == articleIndex,
               LikesOnBoard.boardLikerId == likerId).\
        update(dict(isLikeCancelled = isLikeCancelled))
'''
게시판 검색
'''
def search_articles(Filters, articlesOnBoard, filterCondition, keyWord =''):
    # condition은 All, Id, Title&Content로 나누어서 검새
        
    if filterCondition == Filters[0]: # Filters[0] is '모두'
        articlesOnBoard =dao.query(articlesOnBoard).\
            filter(or_(articlesOnBoard.c.writerId.like('%'+keyWord+'%'), 
                         articlesOnBoard.c.title.like('%'+keyWord+'%'), articlesOnBoard.c.content.like('%'+keyWord+'%')))
    elif filterCondition == Filters[1]: # Filters[1] is '작성자'
        articlesOnBoard =dao.query(articlesOnBoard).\
            filter(articlesOnBoard.c.writerId.like('%'+keyWord+'%'))
    else: # Filters[2] is '제목&내용'
        articlesOnBoard =dao.query(articlesOnBoard).\
            filter(or_(articlesOnBoard.c.title.like('%'+keyWord+'%'), articlesOnBoard.c.content.like('%'+keyWord+'%')))

    return articlesOnBoard
            