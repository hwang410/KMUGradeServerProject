# -*- coding: utf-8 -*-

import copy

from flask import render_template, redirect, url_for, session, request, flash 
from sqlalchemy import func

from GradeServer.database import dao
from GradeServer.model.registeredTeamMembers import RegisteredTeamMembers
from GradeServer.model.teamInvitations import TeamInvitations
from GradeServer.model.teams import Teams
from GradeServer.model.members import Members
from GradeServer.GradeServer_blueprint import GradeServer
from GradeServer.utils import login_required, get_page_pointed, unknown_error, get_message

@GradeServer.route('/team')
@login_required
def team(error =None):
    """ team main page """
    try :
        try :
            # 초대 목록
            teamInvitationRecords =dao.query (TeamInvitations.teamName).filter_by (inviteeId =session['memberId'], isDeleted ='Not-Deleted').all ()
        except Exception :
            # None Type Exception
            teamInvitationRecords =[]
           
        # 내가 속한 팀 정보
        teamNames =dao.query (RegisteredTeamMembers.teamName).filter_by (teamMemberId =session['memberId'], isDeleted ='Not-Deleted').subquery ()
       
        # 내가 속한 팀 인원 수
        teamMemberCounts =dao.query (RegisteredTeamMembers.teamName, func.count (RegisteredTeamMembers.teamMemberId).label ("teamMemberCount")).\
            join (teamNames, RegisteredTeamMembers.teamName == teamNames.c.teamName).\
            filter (RegisteredTeamMembers.isDeleted == 'Not-Deleted').\
            group_by (RegisteredTeamMembers.teamName).subquery ()
        
        # 내가 속한 팀장
        teamMasters =dao.query (RegisteredTeamMembers.teamName, RegisteredTeamMembers.teamMemberId.label ("teamMasterId")).\
            join (teamNames, RegisteredTeamMembers.teamName == teamNames.c.teamName).\
            filter (RegisteredTeamMembers.isTeamMaster == 'Master', RegisteredTeamMembers.isDeleted == 'Not-Deleted').\
            group_by (RegisteredTeamMembers.teamName).subquery ()
    
        # NonType Exception
        try :
            teamRecords =dao.query (teamMasters.c.teamName, teamMasters.c.teamMasterId, teamMemberCounts.c.teamMemberCount).\
                join (teamMemberCounts, teamMasters.c.teamName == teamMemberCounts.c.teamName).all ()
        except Exception :
            # None Type Error
            teamRecords =[]
            
        return render_template('/team.html', teamInvitationRecords =teamInvitationRecords, teamRecords =teamRecords, error =error)
    except Exception :
        # Unknown Error
        return unknown_error ()
    
    
@GradeServer.route('/team_invitation/<teamName>/<accept>')
@login_required
def team_invitation (teamName, accept, error =None) :
    """
    팀 초대 수락 거절
    """
    try :
        # 초대 수락
        if accept == 'accept' :
            newTeamMember =RegisteredTeamMembers (teamName =teamName, teamMemberId =session['memberId'])
            dao.add (newTeamMember)
            dao.query (TeamInvitations).filter_by (teamName =teamName, inviteeId =session['memberId']).update (dict (isDeleted ="Deleted"))
            # Commit Exception
            try :
                dao.commit ()
                flash (teamName +get_message ('acceptInvitee'))
            except Exception :
                dao.rollback ()
                error =get_message ('updateFailed')
        # 초대 걱절    
        else : # reject
            dao.query (TeamInvitations).filter_by (teamName =teamName, inviteeId =session['memberId']).update (dict (isDeleted ="Deleted"))
            # Commit Exception
            try :
                dao.commit ()
                flash (teamName +get_message ('rejectInvitee'))
            except Exception :
                dao.rollback ()
                error =get_message ('updateFailed')
            
        return redirect (url_for('.team', error =error))   
    except Exception :
        # Unknown Error
        return unknown_error ()
    
    
# 팀에 넣을 팀원의 아이디를 저장할 전역 변수
gTeamMembersId  =[]
# 팀 명, 팀 설명
gTeamName, gTeamDescription =None, None
@GradeServer.route('/team/make', methods=['GET', 'POST'])
@login_required
def make_team(error =None):
    """ 
    doesn't have any application of button. 
    you need to make the button app. 
    """
    try :
        global gTeamMembersId, gTeamName, gTeamDescription
        # 자동 완성을 위한 모든 유저기록
        memberRecords =dao.query (Members.memberId, Members.memberName).filter_by (authority ='User').all ()
            
        if request.method == "GET" :
            del gTeamMembersId[:]
            gTeamName, gTeamDescription =None, None
            
            return render_template('/make_team.html', memberRecords =memberRecords)
              
        elif request.method == "POST" :
            # 뷰를 인벨리 데이트 하기전에 인풋값 저장
            gTeamName =request.form['teamName']
            gTeamDescription =request.form['teamDescription'] if request.form['teamDescription'] else None
            
            for form in request.form :
                # Making Team
                if form == "makeTeam" :
                    
                    # 인풋 확인
                    if not gTeamName :
                        return render_template ('/make_team.html', memberRecords =memberRecords,
                                                gTeamMembersId =gTeamMembersId, gTeamDescription =gTeamDescription, error ='팀 명' +get_message ('fillData'))
                    # 중복 팀명 확인
                    if dao.query (Teams.teamName).filter_by (teamName =gTeamName).first () :
                        return render_template ('/make_team.html', memberRecords =memberRecords,
                                                gTeamMembersId =gTeamMembersId, gTeamDescription =gTeamDescription, error =get_message ('existTeamName'))
                    
                    # Insert
                    newTeam =Teams (teamName =gTeamName, teamDescription =gTeamDescription)
                    dao.add (newTeam)
                    # Commit Exception
                    try :
                        dao.commit ()
                        # 마스터 정보
                        newTeamMembers =RegisteredTeamMembers (teamName =gTeamName, teamMemberId =session['memberId'], isTeamMaster ='Master')
                        dao.add (newTeamMembers)
                        dao.commit ()
                        for teamMemberId in gTeamMembersId :
                            newTeamMembers =RegisteredTeamMembers (teamName =gTeamName, teamMemberId =teamMemberId)
                            dao.add (newTeamMembers)
                            dao.commit ()
                        #init
                        del gTeamMembersId[:]
                        gTeamName, gTeamDescription =None, None
                        flash (get_message ('makeTeamSuccessed'))
                        
                        return redirect (url_for('.team'))
                    except Exception :
                        dao.rollback ()
                        error =get_message ('updateFailed')
                    
                # Add Members
                elif form == "addMember" :
                    try :
                        teamMemberId =request.form['teamMemberId'].split ()[0]
                    except Exception :
                        teamMemberId =None
                        
                    # 인풋 폼안에 아이디가 있을 때
                    if teamMemberId :
                        # 존재 하는 사용자 인지 확인
                        if not dao.query (Members.memberId).filter_by (memberId =teamMemberId).first () :
                            error =get_message ('notExists')
                        # 자가 자신 초대 방지
                        elif teamMemberId == session['memberId'] :
                            error =get_message ('notSelf')
                        # 초대 한 애를 또 초대 하는거를 방지
                        elif teamMemberId in gTeamMembersId :
                            error =get_message ('alreadyExists')
                        else :
                            gTeamMembersId.append (teamMemberId)
   
                    # None 값 일 때
                    else :
                        error ='아이디' +get_message ('fillData')
                        
                    break
                # Delete Members
                elif "deleteMember" in form :
                    # form의 name이 deleteMemberi -> i=Index이므로 해당 인덱스 값 제거
                    gTeamMembersId.pop (int (form[-1]))
                    
                    break
                
            return render_template ('/make_team.html', memberRecords =memberRecords,
                                    gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription, error =error)
    except Exception :
        # Unknown Error
        del gTeamMembersId[:]
        gTeamName, gTeamDescription =None, None
        
        return unknown_error ()

@GradeServer.route('/team_information/<teamName>')
@login_required
def team_information(teamName, error =None):
    """
    when you push a team name of team page 
    """
    try :
        # 팀 정보
        try :
            teamInformation =dao.query (Teams).filter_by (teamName =teamName, isDeleted ='Not-Deleted').first ()
        except Exception :
            # None Type Exception
            teamInformation =[]
        # 팀 멤버 정보
        try :
            teamMemberRecords =dao.query (RegisteredTeamMembers.teamMemberId).\
                filter_by (teamName =teamName, isDeleted ='Not-Deleted').\
                    order_by (RegisteredTeamMembers.isTeamMaster.asc(), RegisteredTeamMembers.teamMemberId.asc ()).all ()
        except Exception :
            # None Type Exception
            teamMemberRecords =[]
        
        return render_template('/team_information.html', teamInformation =teamInformation, teamMemberRecords =teamMemberRecords)
    except Exception :
        # Unknown Error
       return unknown_error ()

@GradeServer.route('/team/record/<teamName>')
@login_required
def team_record(teamName, error =None):
    """
    팀 제출 히스토리
    """
    try :
        # user.py ->user_history이용       
        return redirect(url_for('.user_history', memberId =teamName, sortCondition ='submittedDate', pageNum =1))
    except Exception :
        # Unknow Error
        return unknown_error ()


@GradeServer.route('/team/manage/<teamName>', methods=['GET', 'POST'])
@login_required
def team_manage(teamName, error =None):
    
    """
    팀 관리 페이지
    """
    try :
        global gTeamMembersId, gTeamName, gTeamDescription
        try :
            # 자동 완성을 위한 모든 유저기록
            memberRecords =dao.query (Members.memberId, Members.memberName).filter_by (authority ='User').all ()
        except Exception :
            memberRecords =[]
        # 팀 정보
        try :
            teamInformation =dao.query (Teams).filter_by (teamName =teamName, isDeleted ='Not-Deleted').first ()
        except Exception :
            # None Type Exception
            teamInformation =[]
        # 팀 멤버 정보
        try :
            teamMemberRecords =dao.query (RegisteredTeamMembers.teamMemberId).\
                filter_by (teamName =teamName, isDeleted ='Not-Deleted').\
                    order_by (RegisteredTeamMembers.isTeamMaster.asc(), RegisteredTeamMembers.teamMemberId.asc ()).all ()
        except Exception :
            # None Type Exception
            teamMemberRecords =[]
        
        # 팀장이 아닌 애가 왔을 때
        if session['memberId'] != teamMemberRecords[0].teamMemberId :
            return unknown_error (error =get_message ('accessFailed'))
            
        if request.method == "GET" :
            # init
            gTeamMembersId =copy.deepcopy(teamMemberRecords)
            gTeamName, gTeamDescription =None, None
            
            return render_template('/team_manage.html', memberRecords =memberRecords, teamInformation =teamInformation, 
                                   gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription)
              
        elif request.method == "POST" :
            # 인풋이 없다면 기존 이름 가져옴
            gTeamName =request.form['teamName'] if request.form['teamName'] else teamInformation.teamName
            gTeamDescription =request.form['teamDescription'] if request.form['teamDescription'] else teamInformation.teamDescription
            for form in request.form :
                
                # Saving Team
                if form == "saveTeam" :
                    # 팀과 팀 멤버 변경은 동시에 업데이트
                    # Update Team
                    dao.query (Teams).filter_by (teamName =teamName).update (dict (teamName =gTeamName, teamDescription =gTeamDescription))
                    # Update TeamMembers
                    index =0
                    for raw in teamMemberRecords :
                        if index < len (gTeamMembersId) and raw.teamMemberId == gTeamMembersId[index].teamMemberId :
                            index +=1
                        # 삭제 팀원 적용
                        else :
                            dao.query (RegisteredTeamMembers).\
                                filter_by (teamName =teamName, teamMemberId =raw.teamMemberId).update (dict (isDeleted ='Deleted'))
                    # Commit Exception
                    try :
                        dao.commit ()
                    
                        #init
                        del gTeamMembersId[:]
                        gTeamName, gTeamDescription =None, None
                        flash (get_message ('updateSuccessed'))
                    except Exception :
                        dao.rollback ()
                        error =get_message ('udpateFailed')
                        
                    return redirect (url_for('.team', error =error))
                        
                # Invitee Members
                elif form == "inviteeMember" :
                    try :
                        inviteeId =request.form['inviteeId'].split ()[0]
                    except Exception :
                        inviteeId =None
                    # 인풋 폼안에 아이디가 있을 때
                    if inviteeId :
                        # 존재 하는 사용자 인지 확인
                        if not dao.query (Members.memberId).filter_by (memberId =inviteeId).first () :
                            error =get_message ('notExists')
                        # 자가 자신 초대 방지
                        elif inviteeId == session['memberId'] :
                            error =get_message ('notSelf')
                        # 초대 중복 방지
                        elif dao.query (TeamInvitations).\
                            filter_by (teamName =teamName, inviteeId =inviteeId, isDeleted ="Not-Deleted").first () :
                            error =get_message ('alreadyExists')
                        # 팀원 초대 방지
                        elif dao.query (RegisteredTeamMembers.teamMemberId).\
                            filter_by (teamName =teamName, teamMemberId =inviteeId, isDeleted ="Not-Deleted").first () :
                            error =get_message ('notTeamMemberInvitee')
                            
                        # 조건에 충족 될 때
                        else :    
                            newInvitee =TeamInvitations (teamName =teamName, inviteeId =inviteeId)
                            dao.add (newInvitee)
                            # Commit Exception
                            try :
                                dao.commit ()
                                flash (inviteeId +get_message ('inviteeSuccessed'))
                            except Exception :
                                dao.rollback ()
                                error =get_message ('updateFailed')
                    # None 값 일 때
                    else :
                        error ='아이디' +get_message ('fillData')
                        
                    return render_template ('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                    gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription, error =error)
                # Delete Members
                elif "deleteMember" in form :
                    # form의 name이 deleteMemberi -> i=Index이므로 해당 인덱스 값 제거
                    gTeamMembersId.pop (int (form[-1]))
                    
                    return render_template('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                   gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription)
                # Delete Team
                elif form == "deleteTeam" :
                    dao.query (Teams).filter_by (teamName =teamName).update (dict (isDeleted ='Deleted'))
                    dao.query (RegisteredTeamMembers).filter_by (teamName =teamName).update (dict (isDeleted ='Deleted'))
                    dao.query (TeamInvitations).filter_by (teamName =teamName).update (dict (isDeleted ='Deleted'))
                    # Commit Exception
                    try :
                        dao.commit ()
                        #init
                        del gTeamMembersId[:]
                        gTeamName, gTeamDescription =None, None
                        flash (get_message ('removeTeamSuccessed'))
                    except Exception :
                        dao.rollback ()
                        error =get_message ('updateFailed')
                        
                    return redirect (url_for('.team', error =error))
    except Exception :
        # Unknown Error
        del gTeamMembersId[:]
        gTeamName, gTeamDescription =None, None
        
        return unknown_error ()
