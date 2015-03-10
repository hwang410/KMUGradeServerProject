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
from GradeServer.utils import login_required, get_page_pointed

@GradeServer.route('/team')
@login_required
def team():
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
            
        return render_template('/team.html', teamInvitationRecords =teamInvitationRecords, teamRecords =teamRecords)
    except Exception :
        # Unknown Error
        return render_template('/main.html', error ='Sorry Unknown Error!!!')
    
    
@GradeServer.route('/team_invitation/<teamName>/<accept>')
@login_required
def team_invitation (teamName, accept) :
    """
    팀 초대 수락 거절
    """
    try :
        # 초대 수락
        if accept == 'accept' :
            newTeamMember =RegisteredTeamMembers (teamName =teamName, teamMemberId =session['memberId'])
            dao.add (newTeamMember)
            dao.query (TeamInvitations).filter_by (teamName =teamName, inviteeId =session['memberId']).update (dict (isDeleted ="Deleted"))
            dao.commit ()
            flash (teamName +"팀에 합류 되셨습니다.")
        # 초대 걱절    
        else :
            dao.query (TeamInvitations).filter_by (teamName =teamName, inviteeId =session['memberId']).update (dict (isDeleted ="Deleted"))
            dao.commit ()
            flash (teamName +"팀 초대를 거절 하셨습니다.")
            
        return redirect (url_for('.team'))   
    except Exception :
        # Unknown Error
        return render_template('/main.html', error ='Sorry Unknown Error!!!')
    
    
# 팀에 넣을 팀원의 아이디를 저장할 전역 변수
gTeamMembersId  =[]
# 팀 명, 팀 설명
gTeamName, gTeamDescription =None, None
@GradeServer.route('/team/make', methods=['GET', 'POST'])
@login_required
def make_team():
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
                                                gTeamMembersId =gTeamMembersId, gTeamDescription =gTeamDescription, error ="팀 명을 입력해 주세요.")
                    # 중복 팀명 확인
                    if dao.query (Teams.teamName).filter_by (teamName =gTeamName).first () :
                        return render_template ('/make_team.html', memberRecords =memberRecords,
                                                gTeamMembersId =gTeamMembersId, gTeamDescription =gTeamDescription, error ="같은 팀 명이 존재 합니다.")
                    
                    # Insert
                    newTeam =Teams (teamName =gTeamName, teamDescription =gTeamDescription)
                    dao.add (newTeam)
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
                    flash ("팀 만들기 성공!!")
                    
                    return redirect (url_for('.team'))
                # Add Members
                elif form == "addMember" :

                    teamMemberId =request.form['teamMemberId'].split ()[0]
                    # 인풋 폼안에 아이디가 있을 때
                    if teamMemberId :
                        # 존재 하는 사용자 인지 확인
                        if not dao.query (Members.memberId).filter_by (memberId =teamMemberId).first () :
                            return render_template ('/make_team.html', memberRecords =memberRecords,
                                                    gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription,
                                                    error ="해당 사용자가 없습니다.")
                        # 초대 한 애를 또ㅗ 초대 하는거를 방지
                        if teamMemberId in gTeamMembersId :
                            return render_template ('/make_team.html', memberRecords =memberRecords,
                                                    gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription,
                                                    error ="이미 추가된 사용자 압니다.")
                            
                        gTeamMembersId.append (teamMemberId)
                        
                        return render_template ('/make_team.html', memberRecords =memberRecords,
                                                gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription)
                    # None 값 일 때
                    else :
                        return render_template ('/make_team.html', memberRecords =memberRecords,
                                                gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription,
                                                error ="합류 할 아이디를 입력 해 주세요.")
                # Delete Members
                elif "deleteMember" in form :
                    # form의 name이 deleteMemberi -> i=Index이므로 해당 인덱스 값 제거
                    gTeamMembersId.pop (int (form[-1]))
                    
                    return render_template ('/make_team.html', memberRecords =memberRecords,
                                            gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription)
                    
    except Exception :
        # Unknown Error
        del gTeamMembersId[:]
        gTeamName, gTeamDescription =None, None
        
        return render_template('/main.html', error ='Sorry Unknown Error!!!')

@GradeServer.route('/team_information/<teamName>')
@login_required
def team_information(teamName):
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
        return render_template('/main.html', error ='Sorry Unknown Error!!!')

@GradeServer.route('/team/record/<teamName>')
@login_required
def team_record(teamName):
    """
    팀 제출 히스토리
    """
    try :
        # user.py ->user_history이용       
        return redirect(url_for('.user_history', memberId =teamName, pageNum =1))
    except Exception :
        # Unknow Error
        return render_template('/main.html', error ='Sorry Unknown Error!!!')


@GradeServer.route('/team/manage/<teamName>', methods=['GET', 'POST'])
@login_required
def team_manage(teamName):
    
    """
    팀 관리 페이지
    """
    try :
        global gTeamMembersId, gTeamName, gTeamDescription
        # 자동 완성을 위한 모든 유저기록
        memberRecords =dao.query (Members.memberId, Members.memberName).filter_by (authority ='User').all ()
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
            return render_template('/main.html', error ='팀장이 아니어서 접근 할 수 없습니다.')
            
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
                    dao.commit ()
                    
                    #init
                    del gTeamMembersId[:]
                    gTeamName, gTeamDescription =None, None
                    flash ("팀 수정 성공!!")
                    
                    return redirect (url_for('.team'))
                # Invitee Members
                elif form == "inviteeMember" :
                    
                    inviteeId =request.form['inviteeId'].split ()[0]
                    
                    # 인풋 폼안에 아이디가 있을 때
                    if inviteeId :
                        # 존재 하는 사용자 인지 확인
                        if not dao.query (Members.memberId).filter_by (memberId =inviteeId).first () :
                            return render_template ('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                   gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription, error ="해당 사용자가 없습니다.")
                        # 자가 자신 초대 방지
                        if inviteeId == session['memberId'] :
                                return render_template ('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                   gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription, error ="자신을 초대 할 수 없습니다.")
                        # 초대 중복 방지
                        if dao.query (TeamInvitations).\
                            filter_by (teamName =teamName, inviteeId =inviteeId, isDeleted ="Not-Deleted").first () :
                            
                            return render_template ('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                   gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription, error ="이미 최대된 사용자 입니다.")
                        # 팀원 초대 방지
                        if dao.query (RegisteredTeamMembers.teamMemberId).\
                            filter_by (teamName =teamName, teamMemberId =inviteeId, isDeleted ="Not-Deleted").first () :
                            
                            return render_template ('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                    gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription, error ="팀원은 초대 할 수 없습니다.")
                            
                        newInvitee =TeamInvitations (teamName =teamName, inviteeId =inviteeId)
                        dao.add (newInvitee)
                        dao.commit ()
                        flash (inviteeId +"님을 초대 하였습니다.")
                        
                        return render_template('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                   gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription)
                    # None 값 일 때
                    else :
                        return render_template('/team_manage.html',  memberRecords =memberRecords, teamInformation =teamInformation, 
                                   gTeamMembersId =gTeamMembersId, gTeamName =gTeamName, gTeamDescription =gTeamDescription, error ="초대 할 아이디를 입력 해 주세요.")
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
                    dao.commit ()
                    
                    #init
                    del gTeamMembersId[:]
                    gTeamName, gTeamDescription =None, None
                    flash ("팀 삭제 성공!!")
                    
                    return redirect (url_for('.team'))
    except Exception :
        # Unknown Error
        del gTeamMembersId[:]
        gTeamName, gTeamDescription =None, None
        
        return render_template('/main.html', error ='Sorry Unknown Error!!!')
