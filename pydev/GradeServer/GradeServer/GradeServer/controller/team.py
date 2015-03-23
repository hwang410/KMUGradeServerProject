# -*- coding: utf-8 -*-

import copy

from flask import render_template, redirect, url_for, session, request, flash 
from sqlalchemy import func

from GradeServer.utils.loginRequired import login_required
from GradeServer.utils.utilPaging import get_page_pointed
from GradeServer.utils.utilMessages import unknown_error, get_message
from GradeServer.utils.utilQuery import select_all_user, select_match_member
from GradeServer.utils.utils import *

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
@login_required
def team(pageNum = 1, error = None):
    """ team main page """
    try:
        try:
            # 초대 목록
            teamInvitationRecords = dao.query(TeamInvitations.teamName).\
                                        filter(TeamInvitations.inviteeId == session[MEMBER_ID],
                                                  TeamInvitations.isDeleted == NOT_DELETED).all()
        except Exception:
            # None Type Exception
            teamInvitationRecords = []
           
        # 내가 속한 팀 정보
        teamNames = dao.query(RegisteredTeamMembers.teamName).\
                        filter(RegisteredTeamMembers.teamMemberId == session[MEMBER_ID],
                               RegisteredTeamMembers.isDeleted == NOT_DELETED).subquery()
        try:
            count = dao.query(func.count(teamNames.c.teamName).label("count")).first().count
        except Exception:
            count = 0
            
        # 내가 속한 팀 인원 수
        teamMemberCounts = dao.query(RegisteredTeamMembers.teamName,
                                     func.count(RegisteredTeamMembers.teamMemberId).label("teamMemberCount")).\
                                join(teamNames,
                                     RegisteredTeamMembers.teamName == teamNames.c.teamName).\
                                filter(RegisteredTeamMembers.isDeleted == NOT_DELETED).\
                                group_by(RegisteredTeamMembers.teamName).subquery()
                            
        # 내가 속한 팀장
        teamMasters = dao.query(RegisteredTeamMembers.teamName,
                                RegisteredTeamMembers.teamMemberId.label("teamMasterId")).\
                            join(teamNames,
                                 RegisteredTeamMembers.teamName == teamNames.c.teamName).\
                            filter(RegisteredTeamMembers.isTeamMaster == MASTER,
                                   RegisteredTeamMembers.isDeleted == NOT_DELETED).\
                            group_by(RegisteredTeamMembers.teamName).subquery()
    
        # NonType Exception
        try:
            teamRecords = dao.query(teamMasters.c.teamName,
                                    teamMasters.c.teamMasterId,
                                    teamMemberCounts.c.teamMemberCount).\
                                join(teamMemberCounts,
                                     teamMasters.c.teamName == teamMemberCounts.c.teamName).all()
        except Exception:
            # None Type Error
            teamRecords =[]
        
        return render_template(TEAM_HTML,
                               teamInvitationRecords = teamInvitationRecords,
                               teamRecords = teamRecords,
                               pages = get_page_pointed(int(pageNum),
                                                        count),
                               error = error)
    except Exception:
        # Unknown Error
        return unknown_error()
    
    
@GradeServer.route('/team_invitation/<teamName>/<accept>')
@login_required
def team_invitation(teamName, accept, error = None):
    """
    팀 초대 수락 & 거절
    """
    try:
        # Delete Invitee
        dao.query(TeamInvitations).\
            filter(TeamInvitations.teamName == teamName,
                   TeamInvitations.inviteeId == session[MEMBER_ID]).\
            update(dict(isDeleted = DELETED))
        
        # 초대 수락
        if accept == ACCEPT:
            dao.add(insert_team_member_id(teamName,
                                          session[MEMBER_ID]))
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
            
        return redirect(url_for(TEAM,
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
            memberRecords = dao.query(select_all_user()).all()
        except Exception:
            memberRecords = []
            
        if request.method == 'GET':
            del gTeamMembersId[:]
            gTeamName, gTeamDescription = None, None
            
            return render_template(MAKE_TEAM_HTML,
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
                        return render_template(MAKE_TEAM_HTML,
                                               memberRecords = memberRecords,
                                               gTeamMembersId = gTeamMembersId,
                                               gTeamDescription = gTeamDescription,
                                               error = '팀 명'  + get_message('fillData'))
                                        # 중복 팀명 확인
                    try:
                        if dao.query(check_team_name(gTeamName)).first().isDeleted == NOT_DELETED:
                            # don't Exception
                            return render_template(MAKE_TEAM_HTML,
                                                   memberRecords = memberRecords,
                                                   gTeamMembersId = gTeamMembersId,
                                                   gTeamDescription = gTeamDescription,
                                                   error = get_message('existTeamName'))
                        # Deleted Teams
                        else:
                            # Update Team
                            dao.query(Teams).\
                                filter(Teams.teamName == gTeamName).\
                                update(dict(isDeleted = NOT_DELETED))
                    except Exception:
                        # Insert Team
                        newTeam = Teams(teamName = gTeamName,
                                        teamDescription = gTeamDescription)
                        dao.add(newTeam)
                        
                    
                    # Commit Exception
                    try:
                        # this Commit Succeeded Go Next Step
                        dao.commit()
                                                # 마스터 정보
                        print "FDDDD"
                        insert_team_member_id(gTeamName,
                                              session[MEMBER_ID],
                                              MASTER)
                        print "ABCD"
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

                            return redirect(url_for(TEAM,
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
                
            return render_template(MAKE_TEAM_HTML,
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
                                           Teams.isDeleted == NOT_DELETED).first()
        except Exception:
            # None Type Exception
            teamInformation = []
        # 팀 멤버 정보
        try:
            teamMemberRecords = dao.query(RegisteredTeamMembers.teamMemberId).\
                                    filter(RegisteredTeamMembers.teamName == teamName,
                                           RegisteredTeamMembers.isDeleted == NOT_DELETED).\
                                    order_by(RegisteredTeamMembers.isTeamMaster.asc(),
                                             RegisteredTeamMembers.teamMemberId.asc()).all()
        except Exception:
            # None Type Exception
            teamMemberRecords = []
        
        return render_template(TEAM_INFORMATION_HTML,
                               teamInformation = teamInformation,
                               teamMemberRecords = teamMemberRecords)
    except Exception:
        # Unknown Error
        return unknown_error()


@GradeServer.route('/team/record/<teamName>')
@login_required
def team_record(teamName, error = None):
    """
    팀 제출 히스토리
    """
    try:
        # user.py ->user_history이용       
        return redirect(url_for(USER_HISTORY,
                                memberId = teamName,
                                sortCondition = SUBMITTED_DATE,
                                pageNum = 1))
    except Exception:
        # Unknow Error
        return unknown_error()


@GradeServer.route('/team/manage/<teamName>', methods = ['GET', 'POST'])
@login_required
def team_manage(teamName, error = None):
    """
    팀 관리 페이지
    """
    try:
        global gTeamMembersId, gTeamName, gTeamDescription
        try:
            # 자동 완성을 위한 모든 유저기록
            memberRecords = dao.query(select_all_user()).all()
        except Exception:
            memberRecords = []
        # 팀 정보
        try:
            teamInformation = dao.query(Teams).\
                                    filter(Teams.teamName == teamName,
                                           Teams.isDeleted == NOT_DELETED).first()
        except Exception:
            # None Type Exception
            teamInformation = []
        # 팀 멤버 정보
        try:
            teamMemberRecords = dao.query(RegisteredTeamMembers.teamMemberId).\
                                    filter(RegisteredTeamMembers.teamName == teamName,
                                           RegisteredTeamMembers.isDeleted == NOT_DELETED).\
                                    order_by(RegisteredTeamMembers.isTeamMaster.asc(),
                                             RegisteredTeamMembers.teamMemberId.asc()).all()
        except Exception:
            # None Type Exception
            teamMemberRecords = []
        
        # 팀장이 아닌 애가 왔을 때
        if session[MEMBER_ID] != teamMemberRecords[0].teamMemberId:
            return unknown_error(error = get_message('accessFailed'))
            
        if request.method == 'GET':
            # init
            gTeamMembersId = copy.deepcopy(teamMemberRecords)
            gTeamName, gTeamDescription =None, None
            
            return render_template(TEAM_MANAGE_HTML,
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
                    if gTeamName != teamName and not dao.query(check_team_name(gTeamName)).first():
                        dao.query(Teams).\
                            filter(Teams.teamName == teamName).\
                            update(dict(teamName = gTeamName,
                                        teamDescription = gTeamDescription))
                    
                    # Update TeamMembers
                    index = 0
                    for raw in teamMemberRecords:
                        if index < len(gTeamMembersId) and raw.teamMemberId == gTeamMembersId[index].teamMemberId:
                            index += 1
                        # 삭제 팀원 적용
                        else:
                            dao.query(RegisteredTeamMembers).\
                                filter(RegisteredTeamMembers.teamName == teamName,
                                       RegisteredTeamMembers.teamMemberId == raw.teamMemberId).\
                                update(dict(isDeleted = DELETED))
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
                    
                    return redirect(url_for(TEAM,
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
                    
                    return render_template(TEAM_MANAGE_HTML,
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
                    
                    return render_template(TEAM_MANAGE_HTML,
                                           memberRecords = memberRecords,
                                           teamInformation = teamInformation, 
                                           gTeamMembersId = gTeamMembersId,
                                           gTeamName = gTeamName,
                                           gTeamDescription = gTeamDescription)
                # Delete Team
                elif form == 'deleteTeam':
                    dao.query(Teams).\
                        filter(Teams.teamName == teamName).\
                        update(dict(isDeleted = DELETED))
                    dao.query(RegisteredTeamMembers).\
                        filter(RegisteredTeamMembers.teamName == teamName).\
                        update(dict(isDeleted = DELETED))
                    dao.query(TeamInvitations).\
                        filter(TeamInvitations.teamName == teamName).\
                        update(dict(isDeleted = DELETED))
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
                        
                    return redirect(url_for(TEAM,
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
                filter(Teams.teamName == teamName).subquery()
    
    
"""
Check TeamMember Invitee
"""
def check_invitee_member(inviteeId, teamName = None):
        # 인풋 폼안에 아이디가 있을 때
    if inviteeId:
        # 존재 하는 사용자 인지 확인
        if not dao.query(select_match_member(inviteeId)).first():
            return get_message('notExists')
        # 자가 자신 초대 방지
        elif inviteeId == session[MEMBER_ID]:
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
                              TeamInvitations.isDeleted == NOT_DELETED).first():
                return get_message('alreadyExists')
            
                        # 팀원 초대 방지
            elif dao.query(RegisteredTeamMembers.teamMemberId).\
                        filter(RegisteredTeamMembers.teamName == teamName,
                               RegisteredTeamMembers.teamMemberId == inviteeId,
                               RegisteredTeamMembers.isDeleted == NOT_DELETED).first():
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
def insert_team_member_id(teamName, teamMemberId, isTeamMaster = NOT_MASTER):
    # if not exist Records then Insert
    if not dao.query(RegisteredTeamMembers).\
                filter(RegisteredTeamMembers.teamName == teamName,
                       RegisteredTeamMembers.teamMemberId == teamMemberId).first():
        print "ABCDAAAA"
        return dao.add(RegisteredTeamMembers(teamName = teamName,
                                     teamMemberId = teamMemberId,
                                     isTeamMaster = isTeamMaster))
    # else then Update
    else:
        print "SDFSDFAAAA", isTeamMaster
        return dao.query(RegisteredTeamMembers).\
                filter(RegisteredTeamMembers.teamName == teamName,
                       RegisteredTeamMembers.teamMemberId == teamMemberId).\
                update(dict(isDeleted = NOT_DELETED,
                            isTeamMaster =isTeamMaster)) 
        
"""
DB Insert InviteeId
"""
def insert_invitee_id(teamName, inviteeId):
    
    # Update or Insert
    # if not exist then Insert
    if not dao.query(TeamInvitations).\
                filter(TeamInvitations.teamName == teamName,
                       TeamInvitations.inviteeId == inviteeId).first():
        newInvitee = TeamInvitations(teamName = teamName,
                                     inviteeId = inviteeId)
        dao.add(newInvitee)
    # else then Update
    else :
        dao.query(TeamInvitations).\
            filter(TeamInvitations.teamName == teamName,
                   TeamInvitations.inviteeId == inviteeId).\
            update(dict(isDeleted = NOT_DELETED))
    # Commit Exception
    try:
        dao.commit()
        flash(inviteeId + get_message('inviteeSucceeded'))
    except Exception:
        dao.rollback()
        return get_message('updateFailed')
    
    return None