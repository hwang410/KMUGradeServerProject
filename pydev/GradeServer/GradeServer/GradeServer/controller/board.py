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
from GradeServer.utils.utilQuery import select_accept_courses
from GradeServer.utils.utils import *

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
@GradeServer.route('/board/page<pageNum>', methods = ['GET', 'POST'])
@login_required
def board(pageNum):    
    try:
        # 검색시 FilterCondition List
        Filters = ['모두', '작성자', '제목 및 내용']
        # 과목별 게시글
        courses, courseNotices, pages = [], [], []
        articles, articleNotices = [], []
        
        articlesOnBoard = dao.query(ArticlesOnBoard).\
                              filter(ArticlesOnBoard.isDeleted == NOT_DELETED).\
                              subquery()
        # 허용 과목 탐색
        myCourses = select_accept_courses()
        
        # POST
        if request.method == 'POST':
            # 과목 아이디만 가져옴
            try:
                courseId = request.form['courseId'].split()[0]
            except Exception:
                courseId = None
                
            filterCondition = request.form['filterCondition']
            keyWord = request.form['keyWord']
            # courseId가 None이 아닐 때 해당 courseId로 필터링
            if courseId:
                myCourses = dao.query(myCourses).\
                                filter(myCourses.c.courseId == courseId).\
                                subquery()
                articlesOnBoard = dao.query(articlesOnBoard).\
                                      filter(articlesOnBoard.c.courseId == courseId).\
                                      subquery()
            # Like Filterling    
            articlesOnBoard = search_articles(Filters,
                                              articlesOnBoard,
                                              filterCondition = filterCondition,
                                              keyWord = keyWord)
        #과목 목록
        try:
            courseList = dao.query(myCourses).\
                             all()
        except Exception:
            courseList = []
            
        for i in range(0, len(courseList)):
            # 과목의 정보 취득
            # 가져온 과목정에 맞는 게시판 글 취득
            courseSub = dao.query(myCourses.c.courseName,
                                  articlesOnBoard).\
                            filter(myCourses.c.courseId == courseList[i].courseId).\
                            join(articlesOnBoard,
                                 articlesOnBoard.c.courseId == myCourses.c.courseId).\
                            subquery()
            for raw in dao.query(courseSub).all():
                print raw.courseName, raw.isNotice, raw.articleIndex
            # 과목 게시글 모음
            try:
                courses.append(dao.query(get_page_record(dao.query(select_article(courseSub,
                                                                                  NOT_NOTICE)),
                                                        int(pageNum))).\
                                   all())
            except Exception:
                courses.append([])
            try:
                courseNotices.append(dao.query(get_page_record(dao.query(select_article(courseSub,
                                                                                        NOTICE)),
                                                               int(pageNum),
                                                               LIST = 5)).\
                                         all())
            except Exception:
                courseNotices.append([])
            
            # 과목 게시물 페이지 정보 구하기
            pages.append(get_page_pointed(int(pageNum),
                                          len(courses[i])))
        # All Course Subquery
        courseSub = dao.query(myCourses.c.courseName,
                              articlesOnBoard).\
                        join(articlesOnBoard,
                             articlesOnBoard.c.courseId == myCourses.c.courseId).\
                        subquery()
        # All 과목 게시글
        try:
            articles = dao.query(get_page_record(dao.query(select_article(courseSub,
                                                                          NOT_NOTICE)),
                                                 int(pageNum))).\
                           all()
        except Exception:
            articles = []
        # All 과목 공지글    
        try:    
            articleNotices = dao.query(get_page_record(dao.query(select_article(courseSub,
                                                                                NOTICE)),
                                                       int(pageNum),
                                                       LIST = 5)).\
                                 all()
        except Exception:
            articleNotices = []
        # 모드느 과목 페이징 정보 구하기
        allPages = get_page_pointed(int(pageNum),
                                    len(articles))
        # 허용 과목 리스트
        try:
            myCourses = dao.query(myCourses).\
                            all()
        except Exception:
            myCourses = []
        
        return render_template('/board.html',
                               articles = articles,
                               articleNotices =  articleNotices,
                               myCourses = myCourses,
                               courses = courses,
                               courseNotices = courseNotices,
                               allPages = allPages,
                               pages  =pages,
                               Filters = Filters) # classType, condition은 검색 할 때 필요한 변수    
    except Exception:
        return unknown_error()

'''
Board Notice Classification
'''
def select_article(courseSub, isNotice):
    
    return dao.query(courseSub).\
               filter(courseSub.c.isNotice == isNotice).\
               order_by(courseSub.c.articleIndex.desc()).\
               subquery()
 
 
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
        article = dao.query(ArticlesOnBoard).\
                      filter(ArticlesOnBoard.articleIndex == articleIndex).\
                      subquery()
        try:
            article = dao.query(article, 
                                RegisteredCourses.courseName).\
                          join(RegisteredCourses,
                               article.c.courseId == RegisteredCourses.courseId).\
                          first()
        except Exception:
            article = []
            
        # 내가 게시글에 누른 좋아요 정보submissionCount
        try:
            isPostLiked = dao.query(LikesOnBoard.cancelledLike).\
                              filter(LikesOnBoard.boardLikerId == session[MEMBER_ID],
                                     LikesOnBoard.articleIndex == articleIndex).\
                              first() 
        except Exception:
            isPostLiked = NOT_CANCELLED
            
        if isPostLiked:
            isPostLiked = isPostLiked.cancelledLike
        # replies 정보
        try:
            commentRecords = dao.query(RepliesOnBoard).\
                           filter(RepliesOnBoard.isDeleted == NOT_DELETED,
                                  RepliesOnBoard.articleIndex == articleIndex).\
                           order_by(RepliesOnBoard.boardReplyIndex.desc()).\
                           all()
        except Exception:
            commentRecords = []
            
        # 내가 게시글 리플에 누른 좋아요 정보
        try:
            boardReplyLikeCheckRecords = dao.query(LikesOnReplyOfBoard).\
                                      filter(LikesOnReplyOfBoard.articleIndex == articleIndex,
                                             LikesOnReplyOfBoard.boardReplyLikerId == session[MEMBER_ID],
                                             LikesOnReplyOfBoard.cancelledLike == NOT_CANCELLED).\
                                      order_by(LikesOnReplyOfBoard.boardReplyIndex.desc()).\
                                      all()
        except Exception:
            boardReplyLikeCheckRecords = []
        # 나의 댓글 좋아요 여부 적용
        subIndex = 0
        isLikeds = []
        for i in range(0, len(commentRecords)):
            # 나의 댓글 좋아요 정보 비교
            isLikeds.append(dict(isLiked = NOT_LIKED))
            for j in range(subIndex, len(boardReplyLikeCheckRecords)):
                if commentRecords[i].boardReplyIndex == boardReplyLikeCheckRecords[j].boardReplyIndex:
                    isLikeds[i]['isLiked'] = LIKED
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
            update(dict(viewCount = article.viewCount + 1))
        # Commit Exception
        try:
            dao.commit()
            
            return render_template(READ_HTML,
                                   article = article,
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
                    
                    dao.add(update_board_like_count(articleIndex,
                                                    article.sumOfLikeCount + 1))
                    
                    newLike = LikesOnBoard(articleIndex = articleIndex,
                                           boardLikerId = session[MEMBER_ID])
                    dao.add(newLike)
                # 다시 좋아요 누를 때
                elif isPostLiked == CANCELLED:
                    
                    dao.add(update_board_like_count(articleIndex,
                                                    article.sumOfLikeCount + 1))
                    dao.add(update_board_liker_cancelled (articleIndex,
                                                          session[MEMBER_ID],
                                                          NOT_CANCELLED))
                # 좋아요 취소 할 때
                else:  # if it's already exist then change the value of 'pushedLike'
                    
                    dao.add(update_board_like_count(articleIndex,
                                                    article.sumOfLikeCount -1))
                    dao.add(update_board_liker_cancelled (articleIndex,
                                                          session[MEMBER_ID],
                                                          CANCELLED))
                    
                # remove duplicated read count
                dao.query(ArticlesOnBoard).\
                    filter(ArticlesOnBoard.articleIndex == articleIndex).\
                    update(dict(viewCount = article.viewCount - 1))
                
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
                                            articleIndex = article.articleIndex,
                                            boardReplierId = session[MEMBER_ID],
                                            boardReplyContent = request.form['boardCommentWrite'],
                                            boardReplierIp = socket.gethostbyname(socket.gethostname()),
                                            boardRepliedDate = datetime.now())
                dao.add(newComment)
                # remove duplicated read count
                dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount - 1, replyCount =article.replyCount + 1))
                
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
                    if commentLikeCheck.cancelledLike == 'Cancelled':
                        dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[idIndex:])).update(dict(sumOfLikeCount =sumOfLikeCount + 1))
                        dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[idIndex:]),
                                                                  boardReplyLikerId =session['memberId']).update(dict(cancelledLike ='Not-Cancelled'))
                    else:
                        dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[idIndex:]),
                                                                  boardReplyLikerId =session['memberId']).update(dict(cancelledLike ='Cancelled'))
                        dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[idIndex:])).update(dict(sumOfLikeCount=sumOfLikeCount - 1))
                # remove duplicated read count
                dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount - 1))
                
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
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(replyCount=article.replyCount - 1))
                    # remove duplicated read count
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount - 1))
                    
                    flashMsg =get_message('deletedComment')
                    
                    break 
    # Commit Modify
            elif 'modifyBoardComment' in form :
                print "ABC"
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
                        
                    return redirect(url_for(BOARD,
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
            
        return redirect(url_for(READ,
                                articleIndex = articleIndex,
                                error = error))
    
    # Exception View    
    return redirect(url_for(BOARD,
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
            myCourses =dao.query(select_accept_courses()).all()
        except Exception:
            myCourses =[]
            
        # 수정 할 글 정보
        try:
            article =dao.query(ArticlesOnBoard.title, ArticlesOnBoard.content, ArticlesOnBoard.courseId, RegisteredCourses.courseName).\
                join(RegisteredCourses, ArticlesOnBoard.courseId == RegisteredCourses.courseId).\
                filter(ArticlesOnBoard.articleIndex == articleIndex).first()
        except Exception:
            article =[]
        
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
                    courseId =request.form['courseId'].split()[0]
                    title = request.form['title']
                    content = request.form['content']
                    currentDate = datetime.now()
                    currentIP = socket.gethostbyname(socket.gethostname())
                    # 새로 작성
                    if not article:
                        if 'User' in session['authority']: 
                            newPost = ArticlesOnBoard(courseId=courseId, writerId=session['memberId'], title=title, content=content, writtenDate=currentDate, writerIp=currentIP)
                        else:
                            newPost = ArticlesOnBoard(courseId=courseId, writerId=session['memberId'], isNotice='Notice', title=title, content=content, writtenDate=currentDate, writerIp=currentIP)
                        dao.add(newPost)
                        # Commit Exception
                        try:
                            dao.commit()
                            flash(get_message('writtenPost'))
                        except Exception:
                            dao.rollback()
                            error =get_message('updateFailed')
                            
                        return redirect(url_for('.board', pageNum=1))
                    # 게시물 수정    
                    else:
                        dao.query(ArticlesOnBoard).\
                            filter_by(articleIndex =articleIndex).\
                            update(dict(courseId =courseId, title=title, content=content, writtenDate=currentDate, writerIp=currentIP))
                        
                        # Commit Exception
                        try:
                            dao.commit()
                            flash(get_message('modifiedPost'))
                        except Exception:
                            dao.rollback()
                            error =get_message('updateFailed')
                        # request.form['courseId']가 ex)2015100101 전산학 실습 일경우 
                        return redirect(url_for('.read', courseName =request.form['courseId'].split()[1], articleIndex =articleIndex))
                
                except Exception:
                    error =get_message()
 
        return render_template('/write.html', myCourses =myCourses, article =article, title =title, content =content, error=error)
    except Exception:
        # Unknown Error
        return unknown_error()
    
 
'''
  Board Like Count
'''
def update_board_like_count(articleIndex, count):
    return dao.query(ArticlesOnBoard).\
               filter(ArticlesOnBoard.articleIndex == articleIndex).\
               update(dict(sumOfLikeCount = count))   
               
'''
Board LIker Cancelled
'''
def update_board_liker_cancelled(articleIndex, likerId, cancelledLike):
    return dao.query(LikesOnBoard).\
               filter(LikesOnBoard.articleIndex == articleIndex,
                      LikesOnBoard.boardLikerId == likerId).\
               update(dict(cancelledLike = cancelledLike))
'''
게시판 검색
'''
def search_articles(Filters, articlesOnBoard, filterCondition ='All', keyWord =''):
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

    return articlesOnBoard.subquery()
            