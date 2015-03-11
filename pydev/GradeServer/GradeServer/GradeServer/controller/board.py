# -*- coding: utf-8 -*-
"""
    GradeSever.controller.board
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    로그인 확인 데코레이터와 로그인 처리 모듈.

    :copyright: (c) 2015 by KookminUniv

"""

import socket

from flask import render_template, request, session, redirect, url_for
from datetime import datetime
from sqlalchemy import func, or_

from GradeServer.model.articlesOnBoard import ArticlesOnBoard
from GradeServer.model.likesOnBoard import LikesOnBoard
from GradeServer.model.registrations import Registrations
from GradeServer.model.registeredCourses import RegisteredCourses
from GradeServer.model.repliesOnBoard import RepliesOnBoard
from GradeServer.model.likesOnReplyOfBoard import LikesOnReplyOfBoard
from GradeServer.database import dao
from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer 
from GradeServer.utils import login_required, get_page_pointed

@GradeServer.teardown_request
def close_db_session(exception=None):
    """요청이 완료된 후에 db연결에 사용된 세션을 종료함"""
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))


"""
게시판을 과목별 혹은 전체 통합으로
보여주는 페이지
"""
@GradeServer.route('/board/page<pageNum>', methods=['GET', 'POST'])
@login_required
def board(pageNum):    
    try:
        # 검색시 FilterCondition List
        Filters =['모두', '작성자', '제목 및 내용']
        # 과목별 게시글
        courses, courseNotices, pages = [], [], []
        articles, articleNotices = [], []
        
        articlesOnBoard =dao.query (ArticlesOnBoard).\
            filter_by (isDeleted ='Not-Deleted').subquery ()
        # 허용 과목 탐색
        myCourses =get_accept_courses ()
        
        # POST
        if request.method == "POST" :
            # 과목 아이디만 가져옴
            try :
                courseId =request.form['courseId'].split ()[0]
            except Exception :
                courseId =None
            filterCondition =request.form['filterCondition']
            keyWord =request.form['keyWord']
            print courseId, filterCondition, keyWord
            # courseId가 None이 아닐 때 해당 courseId로 필터링
            if courseId  :
                myCourses =dao.query (myCourses).filter_by (courseId =courseId).subquery ()
                articlesOnBoard =dao.query (articlesOnBoard).filter_by (courseId =courseId).subquery ()
            # Like Filterling    
            articlesOnBoard =search_articles(Filters, articlesOnBoard, filterCondition =filterCondition, keyWord =keyWord)
        #과목 목록
        try :
            courseList =dao.query (myCourses).all ()
        except Exception :
            courseList =[]
            
        for i in range (0, len (courseList)) :
            # 과목의 정보 취득
            course = dao.query (myCourses).filter (myCourses.c.courseId == courseList[i].courseId).subquery ()
            # 가져온 과목정에 맞는 게시판 글 취득
            courseSub = dao.query (articlesOnBoard, course.c.courseName).\
                join (course, articlesOnBoard.c.courseId == course.c.courseId).subquery ()
                
            # 과목 게시글 모음
            try :
                courses.append (dao.query (courseSub).\
                                filter (courseSub.c.isNotice == 'Not-Notice').\
                                order_by (courseSub.c.articleIndex.desc ()).all ())
            except Exception :
                #None Type Exception
                courses.append ([])
            try :   
                # 과목 공지글 모음
                courseNotices.append (dao.query (courseSub).\
                                      filter (courseSub.c.isNotice == 'Notice').\
                                      order_by (courseSub.c.articleIndex.desc ()).all ())
            except Exception :
                #None Type Exception
                courseNotices.append ([])
            
            # 과목 게시글 유니온
            articles.extend (courses[i])
            # 과목 게시물 페이지 정보 구하기
            pages.append (get_page_pointed (int (pageNum), len (courses[i])))
            # 과목 공지글 유니온        
            articleNotices.extend (courseNotices[i])
        
        # 모드느 과목 페이징 정보 구하기
        allPages = get_page_pointed (int (pageNum), len (articles))
        # 허용 과목 리스트
        try :
            myCourses =dao.query (myCourses).all ()
        except Exception :
            myCourses =[]
        
        return render_template('/board.html', articles=articles, articleNotices=articleNotices, myCourses =myCourses,
                               courses=courses, courseNotices=courseNotices, allPages =allPages, pages=pages,
                               Filters =Filters) # classType, condition은 검색 할 때 필요한 변수    
    except Exception :
        return render_template('/main.html', error ='Sorry Unknown Error!!!')
 
 
"""
게시글을 눌렀을 때 
글 내용을 보여주는 페이지
"""
@GradeServer.route('/board/<articleIndex>', methods=['GET', 'POST'])
@login_required
def read(articleIndex):
    """ when you push a title of board content """
    # Final 
    try:
        # 게시글 정보
        article = dao.query(ArticlesOnBoard).\
            filter (ArticlesOnBoard.articleIndex == articleIndex).subquery ()
        article =dao.query (article, RegisteredCourses.courseName).\
            join (RegisteredCourses, article.c.courseId == RegisteredCourses.courseId).first ()
            
        # 내가 게시글에 누른 좋아요 정보
        isPostLiked =dao.query(LikesOnBoard.cancelledLike).filter_by(boardLikerId=session['memberId'], articleIndex=articleIndex).first()
        if isPostLiked :
            isPostLiked =isPostLiked.cancelledLike
        # replies 정보
        comments = dao.query(RepliesOnBoard).\
            filter_by(isDeleted='Not-Deleted', articleIndex=articleIndex).\
            order_by (RepliesOnBoard.boardReplyIndex.asc ()).all() 
        # 내가 게시글 리플에 누른 좋아요 정보
        boardReplyLikeCheck = dao.query(LikesOnReplyOfBoard).\
            filter_by (articleIndex=articleIndex, boardReplyLikerId=session['memberId'], cancelledLike ='Not-Cancelled').\
            order_by (LikesOnReplyOfBoard.boardReplyIndex.asc ()).all()
        # 나의 댓글 좋아요 여부 적용
        subIndex = 0
        isLikeds =[]
        for i in range (0, len (comments)) :
            # 나의 댓글 좋아요 정보 비교
            isLikeds.append (dict (isLiked ='Not-Liked'))
            for j in range (subIndex, len (boardReplyLikeCheck)) :
                if comments[i].boardReplyIndex == boardReplyLikeCheck[j].boardReplyIndex :
                    isLikeds[i]['isLiked'] ='Liked'
                    # 다음 시작 루프 인덱스 변경
                    subIndex = j
                    
                    break 
        # deleteCheck = dao.query(BoardReplyLike).filter_by(articleIndex=articleIndex).all()
    except Exception as e:
        Log.error (str(e))
        
    if request.method == 'GET' :
        # 읽은 횟수 카운팅
        dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount + 1))
        # Commit Exception
        try :
            dao.commit()
        except Exception :
            dao.rollback ()
    elif request.method == "POST":
        for form in request.form:
            
            # 게시글 좋아요
            if form == "postLike":
                try:
                    # 좋아요를 누른적 없을 때
                    if not isPostLiked :
                        dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).\
                            update(dict(sumOfLikeCount=article.sumOfLikeCount +1))
                        newLike = LikesOnBoard(articleIndex=articleIndex, boardLikerId=session['memberId'])
                        dao.add(newLike)
                        dao.commit()
                    # 다시 좋아요 누를 때
                    elif isPostLiked == 'Cancelled' :
                        dao.query(ArticlesOnBoard).filter_by(articleIndex =articleIndex).\
                            update(dict(sumOfLikeCount=article.sumOfLikeCount +1))
                        dao.query (LikesOnBoard).filter_by (articleIndex =articleIndex, boardLikerId=session['memberId']).\
                            update (dict (cancelledLike ='Not-Cancelled'))
                        dao.commit()
                    # 좋아요 취소 할 때
                    else:  # if it's already exist then change the value of 'pushedLike'
                        dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).\
                            update(dict(sumOfLikeCount=article.sumOfLikeCount -1))
                        dao.query(LikesOnBoard).filter_by(articleIndex=articleIndex, boardLikerId=session['memberId']).\
                            update(dict(cancelledLike ='Cancelled'))
                        dao.commit()
                    # remove duplicated read count
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount - 1))
                    dao.commit()
                    return redirect(url_for('.read', articleIndex=articleIndex))
                except Exception as e:
                    Log.error (str(e))
                    raise e
            
                # 댓글 달기
            elif form == "comment":
                try:
                    # 현재 게시물의 댓글중에 마지막 인덱스
                    boardReplyIndex =dao.query (func.max (RepliesOnBoard.boardReplyIndex).label ("boardReplyIndex")).\
                        filter_by (articleIndex =articleIndex).first ().boardReplyIndex
                    # 첫 댓글일 경우
                    if not boardReplyIndex :
                        boardReplyIndex =1
                    else :
                        boardReplyIndex +=1
                    
                    # 새로운 댓글 정보
                    newComment = RepliesOnBoard(boardReplyIndex =boardReplyIndex, articleIndex=article.articleIndex, boardReplierId=session['memberId'],
                                                boardReplyContent=request.form['comment'], boardReplierIp=socket.gethostbyname(socket.gethostname()),
                                                boardRepliedDate=datetime.now())
                    dao.add(newComment)
                    # remove duplicated read count
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount - 1, replyCount =article.replyCount +1))
                    dao.commit()
                    return redirect(url_for('.read', articleIndex=articleIndex))
                except Exception as e:
                    Log.error (str(e))
                    raise e

            # 댓글 좋아요
            elif form[:9] == "replyLike":  # the name starts with "replyLike" and it has its unique number
                try:
                    # 해당 댓글의 좋아요 갯수
                    sumOfLikeCount = dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[9:])).first().sumOfLikeCount
                    # 
                    commentLikeCheck = dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[9:]),
                                                                                 boardReplyLikerId =session['memberId']).first()
                    if not commentLikeCheck:  # initial pushing
                        dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[9:])).update(dict(sumOfLikeCount=sumOfLikeCount + 1))
                        newLike = LikesOnReplyOfBoard(articleIndex=articleIndex, boardReplyIndex =int(form[9:]), boardReplyLikerId =session['memberId'])
                        dao.add(newLike)
                        dao.commit()
                    else:
                        if commentLikeCheck.cancelledLike == 'Cancelled':
                            dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[9:])).update(dict(sumOfLikeCount =sumOfLikeCount + 1))
                            dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex =int(form[9:]),
                                                                      boardReplyLikerId =session['memberId']).update(dict(cancelledLike ='Not-Cancelled'))
                            dao.commit()
                        else:
                            dao.query(LikesOnReplyOfBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[9:]),
                                                                      boardReplyLikerId =session['memberId']).update(dict(cancelledLike ='Cancelled'))
                            dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=int(form[9:])).update(dict(sumOfLikeCount=sumOfLikeCount - 1))
                            dao.commit()
                    # remove duplicated read count
                    dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount - 1))
                    dao.commit()
                    return redirect(url_for('.read', articleIndex=articleIndex))
                except Exception as e:
                    Log.error (str(e))
                    raise e
                
            elif form[:13] == "deleteComment":
                try:
                    deleteCheck = dao.query(RepliesOnBoard.isDeleted).filter_by(articleIndex=articleIndex, boardReplyIndex=form[13:]).first()
                    
                    # 삭제 시킬 경우
                    if deleteCheck.isDeleted == 'Not-Deleted':
                        dao.query(RepliesOnBoard).filter_by(articleIndex=articleIndex, boardReplyIndex=form[13:]).update(dict(isDeleted ='Deleted'))
                        dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(replyCount=article.replyCount - 1))
                        # remove duplicated read count
                        dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(viewCount=article.viewCount - 1))
                        dao.commit()
                        return redirect(url_for('.read', articleIndex=articleIndex))
                except Exception as e:
                    Log.error (str(e))
                    raise e
            
            elif form == "deletePost":
                try:
                    deleteCheck = dao.query(ArticlesOnBoard.isDeleted).filter_by(articleIndex=articleIndex).first()
                    if deleteCheck.isDeleted == 'Not-Deleted' :
                        dao.query(ArticlesOnBoard).filter_by(articleIndex=articleIndex).update(dict(isDeleted ='Deleted'))
                        dao.commit()
                        return redirect(url_for('.board', pageNum=1))
                except Exception as e:
                    Log.error (str(e))
                    raise e

    return render_template('/read.html', article=article, comments=comments, isLikeds =isLikeds, isPostLiked =isPostLiked)


"""
게시판에 글을 쓰는 페이지
"""
@GradeServer.route('/board/write/<articleIndex>', methods=['GET', 'POST'])
@login_required
def write(articleIndex):
    error = None
    title, content =None, None
    try :
        # 수강  과목 정보
        try :
            myCourses =dao.query (get_accept_courses()).all ()
        except Exception :
            myCourses =[]
            
        # 수정 할 글 정보
        try :
            article =dao.query (ArticlesOnBoard.title, ArticlesOnBoard.content, ArticlesOnBoard.courseId, RegisteredCourses.courseName).\
                join (RegisteredCourses, ArticlesOnBoard.courseId == RegisteredCourses.courseId).\
                filter (ArticlesOnBoard.articleIndex == articleIndex).first ()
        except Exception :
            article =[]
        
        # 작성시 빈칸 검사
        if request.method == 'POST':
            if not request.form['title']:
                error = "You have to enter a title"
            elif not request.form['content']:
                # 타이틀 가져오기
                title =request.form['title']
                error = "You have to enter a contents"
            elif len(request.form['title']) > 50:
                # 타이틀 가져오기
                title =request.form['title']
                # 내용 가져오기
                content =request.form['content']
                error = "Title is too long. please write less than 50 letters"
            else:
                try:
                    # request.form['courseId']가 ex)2015100101 전산학 실습 일경우 중간의 공백을 기준으로 나눔
                    courseId =request.form['courseId'].split ()[0]
                    title = request.form['title']
                    content = request.form['content']
                    currentDate = datetime.now()
                    currentIP = socket.gethostbyname(socket.gethostname())
                    # 새로 작성
                    if not article :
                        if 'User' in session['authority'] : 
                            newPost = ArticlesOnBoard (courseId=courseId, writerId=session['memberId'], title=title, content=content, writtenDate=currentDate, writerIp=currentIP)
                        else:
                            newPost = ArticlesOnBoard (courseId=courseId, writerId=session['memberId'], isNotice='Notice', title=title, content=content, writtenDate=currentDate, writerIp=currentIP)
                        dao.add (newPost)
                        dao.commit()
                        
                        return redirect(url_for('.board', pageNum=1))
                    # 게시물 수정    
                    else :
                        dao.query (ArticlesOnBoard).\
                            filter_by (articleIndex =articleIndex).\
                            update (dict (courseId =courseId, title=title, content=content, writtenDate=currentDate, writerIp=currentIP))
                        dao.commit ()
                        
                        # request.form['courseId']가 ex)2015100101 전산학 실습 일경우 
                        return redirect (url_for ('.read', courseName =request.form['courseId'].split ()[1], articleIndex =articleIndex))
                
                except Exception :
                    error = "Sorry, unknown Error..."
 
        return render_template('/write.html', error=error, myCourses =myCourses, article =article, title =title, content =content)
    except Exception :
        # Unknown Error
        return render_template('/main.html', error ='Sorry Unknown Error!!!')
    
"""
허용된 과목 정보
"""
def get_accept_courses () :
    # 서버 마스터는 모든 과목에 대해서, 그 외에는 지정된 과목에 대해서
    # Server Master
    if 'ServerAdministrator' in session['authority'] :
        myCourses = dao.query(RegisteredCourses.courseId, RegisteredCourses.courseName)
    # Class Master, User
    elif 'CourseAdministrator' in session['authority'] :
        myCourses = dao.query(RegisteredCourses.courseId, RegisteredCourses.courseName).\
            filter_by(courseAdministratorId=session['memberId'])
    else:
        myCourses = dao.query(Registrations.courseId, RegisteredCourses.courseName).\
            filter (Registrations.memberId == session['memberId']).\
            join(RegisteredCourses, Registrations.courseId == RegisteredCourses.courseId)
            
    return myCourses.subquery ()


"""
게시판 검색
"""
def search_articles (Filters, articlesOnBoard, filterCondition ='All', keyWord ='') :
    # condition은 All, Id, Title&Content로 나누어서 검새
        
    if filterCondition == Filters[0] : # Filters[0] is '모두'
        articlesOnBoard =dao.query (articlesOnBoard).\
            filter (or_ (articlesOnBoard.c.writerId.like ('%'+keyWord+'%'), 
                         articlesOnBoard.c.title.like ('%'+keyWord+'%'), articlesOnBoard.c.content.like ('%'+keyWord+'%')))
    elif filterCondition == Filters[1] : # Filters[1] is '작성자'
        articlesOnBoard =dao.query (articlesOnBoard).\
            filter (articlesOnBoard.c.writerId.like ('%'+keyWord+'%'))
    else : # Filters[2] is '제목&내용'
        articlesOnBoard =dao.query (articlesOnBoard).\
            filter (or_(articlesOnBoard.c.title.like ('%'+keyWord+'%'), articlesOnBoard.c.content.like ('%'+keyWord+'%')))

    return articlesOnBoard.subquery ()
            