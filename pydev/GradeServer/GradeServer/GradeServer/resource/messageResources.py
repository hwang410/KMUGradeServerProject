# -*- coding: utf-8 -*-
from amqp.basic_message import Message

class MessageResources(object):
    from GradeServer.resource import const
    
    '''
    @@ DB Error
    '''
    '''
    =@@ Update error
    '''
    const.ChangingAbolishmentToFalseError = ['폐지정보를 FALSE로 변경에 실패했습니다', 'Error has been occurred while changing abolishment to FALSE']
    const.ChangingAbolishmentToTrueError = ['폐지정보를 TRUE로 변경에 실패했습니다', 'Error has been occurred while changing abolishment to TRUE']
    
    '''
    =@@ Select error
    '''
    const.SearchingDepartmentsError = ['학과 검색에 실패했습니다', 'Error has been occurred while searching departments']
    const.SearchingDepartmentNameError = ['학과 이름 검색에 실패했습니다', 'Error has been occurred while searching department name']
    const.SearchingCollegeNameError = ['대학 이름 검색에 실패했습니다', 'Error has been occurred while searching college name']
    const.SearchingCoursesError = ['과목 검색에 실패했습니다', 'Error has been occurred while searching courses']
    const.SearchingLanguagesError = ['언어 검색에 실패했습니다', 'Error has been occurred while searching languages']
    const.SearchingCourseAdminError = ['과목 담당자 검색에 실패했습니다', 'Error has been occurred while searching course administrators']
    const.SearchingProblemsError = ['문제 검색에 실패했습니다', 'Error has been occurred while searching problems']
    const.SearchingOwnMembersError = ['과목에 등록된 사용자 검색에 실패했습니다', 'Error has been occurred while searching own members']
    const.SearchingExistProblemsError = ['등록된 문제 검색에 실패했습니다', 'Error has been occurred while searching all problems']
    const.SearchingProblemToDeleteError = ['삭제할 문제 검색에 실패했습니다', 'Error has been occurred while searching the problem to delete']
    const.SearchingProblemToEditError = ['수정할 문제 검색에 실패했습니다', 'Error has been occurred while searching the problem to edit']
    const.SearchingSubmissionRecordError = ['제출 기록 검색에 실패했습니다', 'Error has been occurred while searching submission records']
    const.SearchingOwnCoursesError = ['담당 과목 검색에 실패했습니다.', 'Error has been occurred while searching own courses']
    const.SearchingAllMembersError = ['모든 사용자 검색에 실패했습니다', 'Error has been occurred while searching all users']
    
    
    '''
    =@@ Delete error
    '''
    const.DeletingRelationOfCollegeDepartmentError = ['대학, 학과의 관계정보 삭제에 실패했습니다', 'Error has been occurred while deleting relation of college and department']
    const.DeletingRegisteredCourseError = ['등록된 과목 삭제에 실패했습니다', 'Error has been occurred while deleting registered course']
    const.DeletingMemberError = ['사용자 삭제에 실패했습니다', 'Error has been occurred while deleting member']
    const.DeletingProblemError = ['문제 삭제에 실패했습니다', 'Error has been occurred while deleting problem']
    
    '''
    =@@ Insert error
    '''
    const.MakingRelationofDepartmentError = ['대학, 학과 관계정보 생성에 실패했습니다', 'Error has been occurred while making new relation of department']
    const.MakingCollegeError = ['대학 생성에 실패했습니다', 'Error has been occurred while making new college']
    const.MakingDepartmentError = ['학과 생성에 실패했습니다', 'Error has been occurred while making new department']
    const.MakingProblemError = ['문제 생성에 실패했습니다', 'Error has been occurred while adding new problem']
    const.MakingDepartmentsDetailsOfMembersError = ['사용자의 대학, 학과 정보 생성에 실패했습니다', 'Error has been occurred while adding new departments details of members']
    const.MakingLanguageOfCourseError = ['과목의 사용 언어 등록에 실패했습니다.', 'Error has been occurred while adding new language of course']
    const.RegisteringCourseError = ['과목 등록에 실패했습니다', 'Error has been occurred while registering new course']
    const.RegisteringProblemError = ['문제 등록에 실패했습니다', 'Error has been occurred while making a new problem']
    const.MakingProblemRecordError = ['문제에 대한 제출 기록 정보 생성에 실패했습니다', 'Error has been occurred while creating new record']
    const.MakingMemberError = ['사용자 추가에 실패했습니다', 'Error has been occurred while adding new users']
    const.RegisteringMemberError = ['사용자 등록에 실패했습니다', 'Error has been occurred while registering new users']
    
    
    '''
    @@ File system error
    '''
    const.NoSolutionCheckerDirError = ['SOLUTION이나 CHECKER폴더가 없습니다', 'There is no \'SOLUTION\' or \'CHECKER\' directory']
    const.RemovingSpaceError = ['파일 이름에서 공백을 지우는데 실패했습니다', 'Error has been occurred while removing space on file names']
    const.AttachingStringError = ['문자열을 붙이는데 실패했습니다', 'Error has been occurred while attaching string']
    const.GettingCurrentPathError = ['현재 작업 경로를 얻는데 실패했습니다', 'Error has been occurred while getting current path']
    const.ChangingDirError = ['작업 경로를 변경하는데 실패했습니다', 'Error has been occurred while changing directory']
    const.RenamingFileError = ['파일 이름 변경에 실패했습니다', 'Error has been occurred while renaming file']
    const.FileError = ['업로드된 파일에 문제가 있습니다', 'Uploading file error']
    const.DeletionTmpError = ['tmp 폴더를 초기화 하는데 실패했습니다', 'Cannot delete \'tmp\' folder']
    const.ListingFileError = ['파일 목록을 얻는데 실패했습니다', 'Error has been occurred while listing file names']
    const.ClosingProblemFileError = ['문제의 정보파일을 닫는데 실패했습니다', 'Error has been occurred while closing problem meta file']
    const.ReadingProblemFileError = ['문제의 정보파일을 읽는데 실패했습니다', 'Error has been occurred while reading problem meta file(.txt)']
    const.FileNotExist = ['파일이 존재하지 않습니다', 'file doesn\'s exist']
    
    '''
    @@ Requirement Message
    '''
    const.SelectCourse = ['과목 이름을 선택하세요', 'You have to select a course name']
    const.EnterAdmin = ['담당자 아이디를 입력해 주세요', 'You have to enter an administrator ID']
    const.SelectSemester = ['학기를 선택해 주세요', 'You have to select a semester']
    const.SelectLanguage = ['적어도 하나의 언어를 선택해야 합니다', 'You have to select at least one language']
    const.EnterCourseDescription = ['과목 설명을 입력해주세요', 'You have to enter a course description'] 
    const.SelectStartDate = ['시작일을 선택해 주세요', 'You have to select a start date']
    const.SelectEndDate = ['종료일을 선택해 주세요', 'You have to select a end date']
    const.CheckDate = ['종료일은 시작일보다 일러야 합니다', 'Start date should be earlier than end date']
    const.IsNotCourseAdmin = [' 는 과목 담당자가 아닙니다', ' is not registered as a course administrator']
    const.CheckManual = ['매뉴얼을 확인해 주세요', 'check the manual']
    const.TryAgain = ['다시 시도해주세요', 'Try again']
    const.DuplicatedMemberExist = ['중복된 유저가 있습니다', 'There is a duplicated user']
    const.WrongAccess = ['잘못된 접근입니다', 'Wrong access']
    
    '''
    @@ ETC Error
    '''
    const.InsertingFormsIntoArrayError = ['request form으로부터 임시 배열에 값을 저장하는데 실패했습니다', 'Error has been occurred while inserting into temporary array from request form']
    const.InsertingCSVIntoArrayError = ['csv form으로부터 임시 배열에 값을 저장하는데 실패했습니다', 'Error has been occurred while inserting into temporary array from csv form']
    const.InsertingUserFileIntoArray = ['사용자 정보 파일로부터 값을 얻는데 실패했습니다', 'Error has been occurred while inserting values from user file']
    