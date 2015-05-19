# -*- coding: utf-8 -*-

class LanguageResources(object):
    from GradeServer.resource import const
    
    '''
    @@ Main Page
    '''
    const.TopCoder = ['이 주의 탑 코더', 'Top Coder of this week']
    const.HowToUse = ['사용방법', 'How to use']
    const.EmptySpace = ['빈공간', 'Empty Space']
    
    
    '''
    @@ Navigation bar
    '''
    const.Problems = ['문제', 'Problems']
    const.Rank = ['순위', 'Rank']
    const.Board = ['게시판', 'Board']
    const.SignIn = ['로그인', 'Sign in']
    const.Team = ['팀', 'Team']
    const.SignUp = ['회원가입', 'Sign up']


    '''
    ==@@ Problems tab
    '''
    const.CurrentCourse = ['수강중인 수업', 'CURRENT Course']
    const.PastCourse = ['수강했던 수업', 'PAST Course']
    const.none = ['없음', 'None']
    
    
    '''
    ==@@ Member ID tab
    '''
    # common
    const.Account = ['개인 정보', 'Account']
    const.Notice = ['공지 사항', 'Notice']
    const.Manual = ['사용 방법', 'Manual']
    const.SignOut = ['로그 아웃', 'Sign out']
    
    # for administrator
    const.User = ['사용자', 'User']
    const.Service = ['기능', 'Service']
    
    # for server administrator
    const.Server = ['서버', 'Server']
    const.College = ['대학', 'College']
    const.Department = ['학부', 'Department']
    const.Course = ['수업', 'Course']
    
    # for course administrator
    
    # for user
    const.UserRecord = ['제출 정보', 'Record']
    
    
    '''
    @@ Problems page
    '''
    const.ProblemTitle = ['문제이름', 'Title']
    const.Score = ['점수', 'Score']
    const.Status = ['채점상태', 'Status']
    const.DueDate = ['제출기한', 'Due Date']
    const.Count = ['제출횟수', 'Count']
    const.ProblemRecord = ['제출 기록', 'Record']
    
    
    '''
    ==@@ Each problem
    '''
    const.UploadFiles = ['파일로 제출', 'Upload Files']
    const.WriteCode = ['코드 작성', 'Write Code']
    const.ProblemScript = ['문제 보기', 'Problem Script']
    const.Submission = ['제출', 'Submission']
    const.Language = ['사용 언어', 'Language']
    const.Theme = ['에디터 테마', 'Theme']
    const.Limitation = ['제한', 'Limitation']
    const.Time = ['시간', 'Time']
    const.Memory = ['메모리', 'Memory']
    const.Select = ['선택', 'Select']
    const.Runtime = ['실행시간', 'Runtime']
    const.FileSize = ['길이', 'Size']
    const.SubmissionDate = ['제출일', 'Date']
    const.NumberOfFiles = ['파일 개수 선택', 'Select The Number Of Files']
    
    
    '''
    ==@@ User's code
    '''
    const.DownloadCode = ['소스코드 다운로드', 'Download sourcecode']
    
    
    '''
    @@ Rank page
    '''
    const.Ranking = ['순위', 'Ranking']
    const.MemberId = ['ID', 'Member ID']
    const.Comment = ['한마디', 'Comment']
    const.Tries = ['제출 횟수', 'Tries']
    const.SolvedProblems = ['맞춘 문제 수', 'Solved Problems']
    const.Rate = ['정답률', 'Rate']
    const.Find = ['찾기', 'Find']
    
    
    '''
    @@ Board page
    '''
    const.ArticleNum = ['번호', 'Num']
    const.CourseName = ['과목 번호', 'Course Name']
    const.ArticleTitle = ['제목', 'Title']
    const.ArticleMemberId = ['작성자', 'Member ID']
    const.ArticleDate = ['작성일', 'Date']
    const.View = ['조회수', 'View']
    const.Like = ['좋아요', 'Like']
    const.Write = ['글쓰기', 'Write']
    
    
    ''' 
    ==@@ article
    '''
    const.Edit = ['수정', 'Edit']
    
    
    '''
    @@ ID Check
    '''
    const.IdentificationCheck = ['암호 확인', 'Identification Check']
    const.Confirm = ['확인', 'Confirm']
    
    
    '''
    @@ Account
    '''
    const.PersonalInformation = ['개인 정보', 'Personal Information']
    const.ID = ['아이디', 'ID']
    const.Password = ['암호', 'Password']
    const.Name = ['이름', 'Name']
    const.ContactNumber = ['연락처', 'Contact Number']
    const.Email = ['이메일', 'E-mail']
    
    
    '''
    @@ College&Department Management
    '''
    const.Management = ['관리', 'Management']
    const.Check = ['선택', 'Check']
    const.Code = ['코드', 'Code']
    
    
    '''
    @@ Course management
    '''
    const.Number = ['번호', 'Number']
    const.Administrator = ['관리자', 'Administrator']
    const.StartDate = ['시작일', 'Start Date']
    const.FinishDate = ['종료일', 'Finish Date']
    const.OpenDate = ['공개일', 'Open Date']
    const.CloseDate = ['공개종료일', 'Close Date']
    
    
    '''
    ==@@ Course addition
    '''
    const.Semester = ['학기', 'Semester']
    const.Description = ['과목 소개', 'Description']
    const.Done = ['확인', 'Done']
    
    
    '''
    @@ Problem management
    '''
    const.Problem = ['문제', 'Problem']
    const.ProblemId = ['문제번호', 'Problem ID']
    const.Addition = ['추가', 'Addition']
    const.ProblemUpload = ['업로드', 'Upload']
    const.Close = ['닫기', 'Close']
    const.Deletion = ['삭제', 'Deletion']
    
    
    '''
    @@ User management
    '''
    const.UserManagement = ['사용자 관리', 'User Management']
    const.Authority = ['권한', 'Authority']
    const.LastAccess = ['최근 접속일', 'Last Access']
    
    
    '''
    ==@@ User addition
    '''
    const.Indivisual = ['개별 추가', 'Indivisual']
    const.Group = ['그룹 추가', 'Group']
    const.AddLine = ['줄 추가', 'Add line']
    
    
    '''
    @@ Submission management
    '''
    const.Detail = ['자세히', 'Detail']
    const.DetailMode = ['자세히 보기', 'Detail mode']
    const.Summary = ['요약', 'Summary']
    const.SummaryMode = ['간략히 보기', 'Summary mode']
    const.History = ['기록', 'History']

    '''
    @@ Service management
    '''
    const.Judging = ['채점', 'Judging']