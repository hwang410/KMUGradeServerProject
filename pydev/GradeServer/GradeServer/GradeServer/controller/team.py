# -*- coding: utf-8 -*-

import copy

from flask import render_template, redirect, url_for, session, request, flash 
from sqlalchemy import func

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.checkInvalidAccess import check_invalid_access
from GradeServer.utils.utilPaging import get_page_pointed, get_page_record
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.utilQuery import select_all_users, select_match_members_of_course, select_match_member

from GradeServer.resource.enumResources import ENUMResources
from GradeServer.resource.setResources import SETResources
from GradeServer.resource.htmlResources import HTMLResources
from GradeServer.resource.routeResources import RouteResources
from GradeServer.resource.otherResources import OtherResources
from GradeServer.resource.sessionResources import SessionResources

from GradeServer.database import dao
from GradeServer.model.registeredTeamMembers import RegisteredTeamMembers
from GradeServer.model.teamInvitations import TeamInvitations
from GradeServer.model.teams import Teams

from GradeServer.GradeServer_logger import Log
from GradeServer.GradeServer_blueprint import GradeServer


@GradeServer.teardown_request
def close_db_session(exception = None):
    """요청이 완료된 후에 db연결에 사용된 세션을 종료함"""
    try:
        dao.remove()
    except Exception as e:
        Log.error(str(e))
        
        
@GradeServer.route('/team/page<pageNum>')
@check_invalid_access
@login_required
def team(pageNum = 1, error = None):
    """ team main page """
    try:
        try:
            # 초대 목록
            teamInvitationRecords = dao.query(TeamInvitations.teamName).\
                                        filter(TeamInvitations.inviteeId == session[SessionResources().const.MEMBER_ID],
                                                  TeamInvitations.isDeleted == ENUMResources().const.FALSE).\
                                        all()
        except Exception:
            # None Type Exception
            teamInvitationRecords = []
           
        # 내가 속한 팀 정보
        teamNames = dao.query(RegisteredTeamMembers.teamName).\
                        filter(RegisteredTeamMembers.teamMemberId == session[SessionResources().const.MEMBER_ID],
                               RegisteredTeamMembers.isDeleted == ENUMResources().const.FALSE).\
                        subquery()
        try:
            count = dao.query(func.count(teamNames.c.teamName).label("count")).\
                        first().\
                        count
        except Exception:
            count = 0
            
        # 내가 속한 팀 인원 수
        teamMemberCounts = dao.query(RegisteredTeamMembers.teamName,
                                     func.count(RegisteredTeamMembers.teamMemberId).label("teamMemberCount")).\
                               join(teamNames,
                                    RegisteredTeamMembers.teamName == teamNames.c.teamName).\
                               filter(RegisteredTeamMembers.isDeleted == ENUMResources().const.FALSE).\
                               group_by(RegisteredTeamMembers.teamName).\
                               subquery()
                            
        # 내가 속한 팀장
        teamMasters = dao.query(RegisteredTeamMembers.teamName,
                                RegisteredTeamMembers.teamMemberId.label("teamMasterId")).\
                          join(teamNames,
                               RegisteredTeamMembers.teamName == teamNames.c.teamName).\
                          filter(RegisteredTeamMembers.isTeamMaster == ENUMResources().const.TRUE,
                                 RegisteredTeamMembers.isDeleted == ENUMResources().const.FALSE).\
                          group_by(RegisteredTeamMembers.teamName).\
                          subquery()
    
        # NonType Exception
        try:
            # order and get record
            teamRecords = get_page_record(dao.query(teamMasters.c.teamName,
                                                    teamMasters.c.teamMasterId,
                                                    teamMemberCounts.c.teamMemberCount).\
                                              join(teamMemberCounts,
                                                   teamMasters.c.teamName == teamMemberCounts.c.teamName).\
                                              order_by(teamMasters.c.teamName.asc()),
                                          pageNum = int(pageNum)).\
                          all()
        except Exception:
            # None Type Error
            teamRecords =[]
        
        return render_template(HTMLResources().const.TEAM_HTML,
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               teamInvitationRecords = teamInvitationRecords,
                               teamRecords = teamRecords,
                               pages = get_page_pointed(pageNum = int(pageNum),
                                                        count = count),
                               error = error)
    except Exception:
        # Unknown Error
        return unknown_error()
    
    
@GradeServer.route('/team_invitation/<teamName>/<accept>')
@check_invalid_access
@login_required
def team_invitation(teamName, accept, error = None):
    """
    팀 초대 수락 & 거절
    """
    try:
        # Delete Invitee
        dao.query(TeamInvitations).\
            filter(TeamInvitations.teamName == teamName,
                   TeamInvitations.inviteeId == session[SessionResources().const.MEMBER_ID]).\
            update(dict(isDeleted = ENUMResources().const.TRUE))
        
        # 초대 수락
        if accept == OtherResources().const.ACCEPT:
            insert_team_member_id(teamName,
                                  session[SessionResources().const.MEMBER_ID])
            # Commit Exception
            try:
                dao.commit()
                flash(teamName + get_message('acceptInvitee'))
            except Exception:
                dao.rollback()
                error = get_message('updateFailed')
        # 초대 걱절    
        else: # elif == REJECT:
            # Commit Exception
            try:
                dao.commit()
                flash(teamName + get_message('rejectInvitee'))
            except Exception:
                dao.rollback()
                error = get_message('updateFailed')
            
        return redirect(url_for(RouteResources().const.TEAM,
                                pageNum = 1,
                                error = error))   
    except Exception:
        # Unknown Error
        return unknown_error()
    
    
# 팀에 넣을 팀원의 아이디를 저장할 전역 변수
gTeamMembersId  =[]
# 팀 명, 팀 설명
gTeamName, gTeamDescription = None, None
@GradeServer.route('/team/make', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def make_team(error = None):
    """ 
    doesn't have any application of button. 
    you need to make the button app. 
    """
    try:
        global gTeamMembersId, gTeamName, gTeamDescription
                # 자동 완성을 위한 모든 유저기록
        try :
            memberRecords = select_all_users().all()
        except Exception:
            memberRecords = []
        
        print "?", memberRecords
        for k in memberRecords:
            print k.memberId
                
        if request.method == 'GET':
            del gTeamMembersId[:]
            gTeamName, gTeamDescription = None, None
            
            return render_template(HTMLResources().const.TEAM_MAKE_HTML,
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
                                   memberRecords = memberRecords)
              
        elif request.method == 'POST':
                # 뷰를 인벨리 데이트 하기전에 인풋값 저장
            gTeamName = request.form['teamName']
            gTeamDescription = request.form['teamDescription'] if request.form['teamDescription'] else None
            
            for form in request.form:
                # Making Team
                if form == 'makeTeam':
                    
                                        # 인풋 확인
                    if not gTeamName:
                        return render_template(HTMLResources().const.TEAM_MAKE_HTML,
                                               SETResources = SETResources,
                                               SessionResources = SessionResources,
                                               memberRecords = memberRecords,
                                               gTeamMembersId = gTeamMembersId,
                                               gTeamDescription = gTeamDescription,
                                               error = '팀 명'  + get_message('fillData'))
                                        # 중복 팀명 확인
                    try:
                        if check_team_name(gTeamName).first().\
                                                      isDeleted == ENUMResources().const.FALSE:
                            # don't Exception
                            return render_template(HTMLResources().const.TEAM_MAKE_HTML,
                                                   SETResources = SETResources,
                                                   SessionResources = SessionResources,
                                                   memberRecords = memberRecords,
                                                   gTeamMembersId = gTeamMembersId,
                                                   gTeamDescription = gTeamDescription,
                                                   error = get_message('existTeamName'))
                        # Deleted Teams
                        else:
                            # Update Team
                            dao.query(Teams).\
                                filter(Teams.teamName == gTeamName).\
                                update(dict(isDeleted = ENUMResources().const.FALSE))
                    except Exception:
                        # Insert Team
                        newTeam = Teams(teamName = gTeamName,
                                        teamDescription = gTeamDescription)
                        dao.add(newTeam)
                        
                    
                    # Commit Exception
                    try:
                        # this Commit Succeeded Go Next Step
                        dao.commit()
                                                # 마스터 정보first().teamName
                        insert_team_member_id(gTeamName,
                                              session[SessionResources().const.MEMBER_ID],
                                              ENUMResources().const.TRUE)
                        # this Commit Succeeded Go Next Step
                        try:
                            dao.commit()
                            for inviteeId in gTeamMembersId:
                                error = insert_invitee_id(gTeamName,
                                                          inviteeId)
                                # Exception Check
                                if error:
                                    break
                            #init
                            del gTeamMembersId[:]
                            gTeamName, gTeamDescription = None, None
                            flash(get_message('makeTeamSucceeded'))

                            return redirect(url_for(RouteResources().const.TEAM,
                                                    pageNum = 1))
                        except Exception:
                            dao.rollback()
                            error = get_message('updateFailed')
                    except Exception:
                        dao.rollback()
                        error = get_message('updateFailed')
                    
                # Add Members
                elif form == 'inviteeMember':
                    try:
                        inviteeId = request.form['inviteeId'].split()[0]
                    except Exception:
                        inviteeId = None
                    # teamMember Invitee
                    error = check_invitee_member(inviteeId)
                        
                    break
                # Delete Members
                elif 'deleteInviteeMember' in form:
                    # form의 name이 deleteMemberi -> i=Index이므로 해당 인덱스 값 제거
                    gTeamMembersId.pop(int(form[-1]))
                    
                    break
                
            return render_template(HTMLResources().const.TEAM_MAKE_HTML,
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
                                   memberRecords = memberRecords,
                                   gTeamMembersId = gTeamMembersId,
                                   gTeamName = gTeamName,
                                   gTeamDescription = gTeamDescription,
                                   error = error)
    except Exception:
        # Unknown Error
        del gTeamMembersId[:]
        gTeamName, gTeamDescription = None, None
        
        return unknown_error()

@GradeServer.route('/team_information/<teamName>')
@check_invalid_access
@login_required
def team_information(teamName, error = None):
    """
    when you push a team name of team page 
    """
    try:
        # 팀 정보
        try:
            teamInformation = dao.query(Teams).\
                                    filter(Teams.teamName == teamName,
                                           Teams.isDeleted == ENUMResources().const.FALSE).first()
        except Exception:
            # None Type Exception
            teamInformation = []
        # 팀 멤버 정보
        try:
            teamMemberRecords = dao.query(RegisteredTeamMembers.teamMemberId).\
                                    filter(RegisteredTeamMembers.teamName == teamName,
                                           RegisteredTeamMembers.isDeleted == ENUMResources().const.FALSE).\
                                    order_by(RegisteredTeamMembers.isTeamMaster.asc(),
                                             RegisteredTeamMembers.teamMemberId.asc()).all()
        except Exception:
            # None Type Exception
            teamMemberRecords = []
        
        return render_template(HTMLResources().const.TEAM_INFORMATION_HTML,
                               SETResources = SETResources,
                               SessionResources = SessionResources,
                               teamInformation = teamInformation,
                               teamMemberRecords = teamMemberRecords)
    except Exception:
        # Unknown Error
        return unknown_error()


@GradeServer.route('/team/record/<teamName>')
@check_invalid_access
@login_required
def team_record(teamName, error = None):
    """
    팀 제출 히스토리
    """
    try:
        # user.py ->user_history이용       
        return redirect(url_for(RouteResources().const.USER_HISTORY,
                                SETResources = SETResources,
                                memberId = teamName,
                                sortCondition = OtherResources().const.SUBMISSION_DATE,
                                pageNum = 1))
    except Exception:
        # Unknow Error
        return unknown_error()


@GradeServer.route('/team/manage/<teamName>', methods = ['GET', 'POST'])
@check_invalid_access
@login_required
def team_manage(teamName, error = None):
    """
    팀 관리 페이지
    """
    try:
        global gTeamMembersId, gTeamName, gTeamDescription
        try:
            # 자동 완성을 위한 모든 유저기록
            memberRecords = dao.query(select_all_user().subqeury()).\
                                all()
        except Exception:
            memberRecords = []
        # 팀 정보
        try:
            teamInformation = dao.query(Teams).\
                                    filter(Teams.teamName == teamName,
                                           Teams.isDeleted == ENUMResources().const.FALSE).first()
        except Exception:
            # None Type Exception
            teamInformation = []
        # 팀 멤버 정보
        try:
            teamMemberRecords = dao.query(RegisteredTeamMembers.teamMemberId).\
                                    filter(RegisteredTeamMembers.teamName == teamName,
                                           RegisteredTeamMembers.isDeleted == ENUMResources().const.FALSE).\
                                    order_by(RegisteredTeamMembers.isTeamMaster.asc(),
                                             RegisteredTeamMembers.teamMemberId.asc()).all()
        except Exception:
            # None Type Exception
            teamMemberRecords = []
        
        # 팀장이 아닌 애가 왔을 때
        if session[SessionResources().const.MEMBER_ID] != teamMemberRecords[0].teamMemberId:
            return unknown_error(error = get_message('accessFailed'))
            
        if request.method == 'GET':
            # init
            gTeamMembersId = copy.deepcopy(teamMemberRecords)
            gTeamName, gTeamDescription =None, None
            
            return render_template(HTMLResources().const.TEAM_MANAGE_HTML,
                                   SETResources = SETResources,
                                   SessionResources = SessionResources,
                                   memberRecords = memberRecords,
                                   teamInformation =teamInformation, 
                                   gTeamMembersId = gTeamMembersId,
                                   gTeamName = gTeamName,
                                   gTeamDescription = gTeamDescription)
              
        elif request.method == 'POST':
            # 인풋이 없다면 기존 이름 가져옴
            gTeamName =request.form['teamName'] if request.form['teamName'] else teamInformation.teamName
            gTeamDescription = request.form['teamDescription'] if request.form['teamDescription'] else teamInformation.teamDescription
            for form in request.form:
                
                # Saving Team
                if form == 'saveTeam':
                    # 팀과 팀 멤버 변경은 동시에 업데이트
                    # Update Team
                                        # 중복 팀명 확인
                    if gTeamName != teamName and\
                       not dao.query(check_team_name(gTeamName).subquery()).\
                               first():
                        dao.query(Teams).\
                            filter(Teams.teamName == teamName).\
                            update(dict(teamName = gTeamName,
                                        teamDescription = gTeamDescription))
                    
                    # Update TeamMembers
                    index = 0
                    for raw in teamMemberRecords:
                        if index < len(gTeamMembersId) and\
                           raw.teamMemberId == gTeamMembersId[index].teamMemberId:
                            index += 1
                        # 삭제 팀원 적용
                        else:
                            dao.query(RegisteredTeamMembers).\
                                filter(RegisteredTeamMembers.teamName == teamName,
                                       RegisteredTeamMembers.teamMemberId == raw.teamMemberId).\
                                update(dict(isDeleted = ENUMResources().const.TRUE))
                    # Commit Exception
                    try:
                        dao.commit()
                        #init
                        del gTeamMembersId[:]
                        gTeamName, gTeamDescription = None, None
                        flash(get_message('updateSucceeded'))
                    except Exception:
                        dao.rollback()
                        error =get_message('updateFailed')
                    
                    return redirect(url_for(RouteResources().const.TEAM,
                                            pageNum = 1,
                                            error = error))
                        
                # Invitee Members
                elif form == 'inviteeMember':
                    try:
                        inviteeId = request.form['inviteeId'].split()[0]
                    except Exception:
                        inviteeId = None
                    # teamMember Invitee
                    error = check_invitee_member(inviteeId,
                                                 teamName)
                    
                    return render_template(HTMLResources().const.TEAM_MANAGE_HTML,
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           memberRecords = memberRecords,
                                           teamInformation = teamInformation, 
                                           gTeamMembersId = gTeamMembersId,
                                           gTeamName = gTeamName,
                                           gTeamDescription = gTeamDescription,
                                           error = error)
                # Delete Members
                elif 'deleteMember' in form:
                    # form의 name이 deleteMemberi -> i=Index이므로 해당 인덱스 값 제거
                    gTeamMembersId.pop(int(form[-1]))
                    
                    return render_template(HTMLResources().const.TEAM_MANAGE_HTML,
                                           SETResources = SETResources,
                                           SessionResources = SessionResources,
                                           memberRecords = memberRecords,
                                           teamInformation = teamInformation, 
                                           gTeamMembersId = gTeamMembersId,
                                           gTeamName = gTeamName,
                                           gTeamDescription = gTeamDescription)
                # Delete Team
                elif form == 'deleteTeam':
                    dao.query(Teams).\
                        filter(Teams.teamName == teamName).\
                        update(dict(isDeleted = ENUMResources().const.TRUE))
                    dao.query(RegisteredTeamMembers).\
                        filter(RegisteredTeamMembers.teamName == teamName).\
                        update(dict(isDeleted = ENUMResources().const.TRUE))
                    dao.query(TeamInvitations).\
                        filter(TeamInvitations.teamName == teamName).\
                        update(dict(isDeleted = ENUMResources().const.TRUE))
                    # Commit Exception
                    try:
                        dao.commit()
                        #init
                        del gTeamMembersId[:]
                        gTeamName, gTeamDescription = None, None
                        flash(get_message('removeTeamSucceeded'))
                    except Exception:
                        dao.rollback()
                        error = get_message('updateFailed')
                        
                    return redirect(url_for(RouteResources().const.TEAM,
                                            pageNum = 1,
                                            error =error))
    except Exception:
        # Unknown Error
        del gTeamMembersId[:]
        gTeamName, gTeamDescription = None, None
        
        return unknown_error()
"""
Check TeamName
"""
def check_team_name(teamName):
    return dao.query(Teams).\
               filter(Teams.teamName == teamName)
    
    
"""
Check TeamMember Invitee
"""
def check_invitee_member(inviteeId, teamName = None):
        # 인풋 폼안에 아이디가 있을 때
    if inviteeId:
        # 존재 하는 사용자 인지 확인
        if not dao.query(select_match_member(memberId = inviteeId).subquery()).\
                   first():
            
            return get_message('notExists')
        # 자가 자신 초대 방지
        elif inviteeId == session[SessionResources().const.MEMBER_ID]:
            return get_message('notSelf')
        # MakeTeam In Invitee
        elif not teamName:
                        # 초대 한 애를 또 초대 하는거를 방지
            if inviteeId in gTeamMembersId:
                return get_message('alreadyExists') 
            # Invitee Id Add
            gTeamMembersId.append(inviteeId)
            
            return None
        # ManageTeam In Invitee
        else:
                        # 초대 중복 방지
            if dao.query(TeamInvitations).\
                   filter(TeamInvitations.teamName == teamName,
                              TeamInvitations.inviteeId == inviteeId,
                              TeamInvitations.isDeleted == ENUMResources().const.FALSE).\
                   first():
                
                return get_message('alreadyExists')
            
                        # 팀원 초대 방지
            elif dao.query(RegisteredTeamMembers.teamMemberId).\
                     filter(RegisteredTeamMembers.teamName == teamName,
                            RegisteredTeamMembers.teamMemberId == inviteeId,
                            RegisteredTeamMembers.isDeleted == ENUMResources().const.FALSE).\
                     first():
                
                return get_message('notTeamMemberInvitee')
                        # 조건에 충족 될 때
            else:    
                return insert_invitee_id(teamName,
                                         inviteeId)
    # None 값 일 때
    else:
        return '아이디'  + get_message('fillData')
    
    
"""
 DB Insert Team Members
"""
def insert_team_member_id(teamName, teamMemberId, isTeamMaster = ENUMResources().const.FALSE):
    # if not exist Records then Insert
    if not dao.query(RegisteredTeamMembers).\
               filter(RegisteredTeamMembers.teamName == teamName,
                      RegisteredTeamMembers.teamMemberId == teamMemberId).\
               first():
        dao.add(RegisteredTeamMembers(teamName = teamName,
                                      teamMemberId = teamMemberId,
                                      isTeamMaster = isTeamMaster))
        dao.commit()
    # else then Update
    else:
        dao.query(RegisteredTeamMembers).\
            filter(RegisteredTeamMembers.teamName == teamName,
                   RegisteredTeamMembers.teamMemberId == teamMemberId).\
            update(dict(isDeleted = ENUMResources().const.FALSE,
                        isTeamMaster =isTeamMaster)) 
        
"""
DB Insert InviteeId
"""
def insert_invitee_id(teamName, inviteeId):
    
    # Update or Insert
    # if not exist then Insert
    if not dao.query(TeamInvitations).\
               filter(TeamInvitations.teamName == teamName,
                      TeamInvitations.inviteeId == inviteeId).\
               first():
        newInvitee = TeamInvitations(teamName = teamName,
                                     inviteeId = inviteeId)
        dao.add(newInvitee)
    # else then Update
    else :
        dao.query(TeamInvitations).\
            filter(TeamInvitations.teamName == teamName,
                   TeamInvitations.inviteeId == inviteeId).\
            update(dict(isDeleted = ENUMResources().const.FaLSE))
    # Commit Exception
    try:
        dao.commit()
        flash(inviteeId + get_message('inviteeSucceeded'))
    except Exception:
        dao.rollback()
        return get_message('updateFailed')
    
    return None