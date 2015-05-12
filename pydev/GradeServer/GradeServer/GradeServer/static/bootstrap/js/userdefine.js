		/* 
		fill every "here" sign using jinja2 template

		when you click 'Title', link to its information
		*/

// the way of submit(default)
$(window).load(function(){
	document.getElementsByClassName("positionOfForms")[0].innerHTML 
	= "Upload File Form<br>"+"<form class='file_upload' method='post'><input type='button' value='file'><br><button id='submitCode' type='submit' class='fluid-btn'>Submit</button></form>";
});

// submit button event
function showSourceCodeForm(parent){
	var className = parent.className;
	// class name is not the unique value. 
	// so need to put index of its last to use the exact value
	var target = document.getElementsByClassName("positionOfForms")[0];
	if(className == "file_upload btn"){
		target.innerHTML = "Upload File Form<br>"+"<form class='file_upload' method='post'><input type='button' value='file'><br><button id='submitCode' type='submit' class='fluid-btn'>Submit</button></form>";
	}
	else if(className == "code_writing btn"){
		target.innerHTML = "Write Code Form<br>"+"<form class='code_writing' method='post'><textarea class='content input-xxlarge' style='margin-left:0px'></textarea><br><button id='submitCode' type='submit' class='fluid-btn'>Submit</button></form>";
	}
	else{
		alert("error");
	}
}

// load function after all window's loaded
$(window).load(function(){
	window.onload = function(){
		setLegend();
	}
	function setLegend(){
			// solved, wrong answer, time over, compile error, runtime error
			var colors = new Array("#0c274c", "#18709c", "#19bdc4", "#fff6ee", "#ef4089");
			var errors = new Array("Solved", "Wrong Answer", "Time Over", "Compile Error", "Runtime Error");
			var target = document.getElementById("legend-box");
			for(var i=0;i<colors.length;i++){
				if(i==3) target.innerHTML += "<span class='label' style='color:black;background-color:"+colors[i]+"'>"+errors[i]+"</span>"+"<br>";
				else target.innerHTML += "<span class='label' style='background-color:"+colors[i]+"'>"+errors[i]+"</span>"+"<br>";
			}
		}
});

var textarea = $('#getCode');

// language change
function selectLanguage(selectObj) {
	var mode;
	var theme;
	if(selectObj.value == 1 || selectObj.value == 2){ mode = "c_cpp"; }
	if(selectObj.value == 3){ mode = "java"; }
	if(selectObj.value == 4 || selectObj.value == 5){ mode = "python"; }
	if(selectObj.value == 6){ theme = "chrome"; }
	if(selectObj.value == 7){ theme = "clouds"; }
	if(selectObj.value == 8){ theme = "eclipse"; }
	if(selectObj.value == 9){ theme = "github"; }
	if(selectObj.value == 10){ theme = "monokai"; }
	if(selectObj.value == 11){ theme = "textmate"; }
	if(selectObj.value == 12){ theme = "tomorrow"; }

	editor.session.setMode("ace/mode/" + mode);
	editor.setTheme("ace/theme/" + theme);
}

//dropzone
Dropzone.options.myDropzoneC = { // The camelized version of the ID of the form element
	
	// The configuration we've talked about above
	autoProcessQueue: false, // auto false
	uploadMultiple: true,	// 
	parallelUploads: 10,	// 
	maxFiles: 10,			// 
	maxFilesize: 0.5, 
	addRemoveLinks: true,	// Remove 
	acceptedFiles: ".c, .h",		// 

		// The setting up of the dropzone
		// submit-all 
		//	processQueue()
	init: function() {
		var myDropzone = this;
		$("#submit-all").click(function (e) {
			myDropzone.processQueue();
				});
				
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			location.href = parent.document.referrer;
	 	});
	}
}

Dropzone.options.myDropzoneCpp = { // The camelized version of the ID of the form element
	
	// The configuration we've talked about above
		autoProcessQueue: false, // auto false
		uploadMultiple: true,	// 
		parallelUploads: 10,	// 
		maxFiles: 10,			//
		maxFilesize: 0.5, 
		addRemoveLinks: true,	// Remove 
		acceptedFiles: ".cpp, .h",		// 

		// The setting up of the dropzone
		// submit-all 
		//	processQueue()
		init: function() {
		var myDropzone = this;
		$("#submit-all").click(function (e) {
			myDropzone.processQueue();
				});
				
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			address = "http://localhost/problemList/" + response;
			location.href = parent.document.referrer;
	 	});
	}
}

Dropzone.options.myDropzoneJAVA = { // The camelized version of the ID of the form element
	
	// The configuration we've talked about above
		autoProcessQueue: false, // auto false
		uploadMultiple: true,	// 
		parallelUploads: 10,	// 
		maxFiles: 10,			// 
		maxFilesize: 0.5,
		addRemoveLinks: true,	// Remove 
		acceptedFiles: ".java, .class, .jar",		// 

		// The setting up of the dropzone
		// submit-all 
		//	processQueue()
		init: function() {
		var myDropzone = this;
		$("#submit-all").click(function (e) {
			myDropzone.processQueue();
				});
				
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			location.href = parent.document.referrer;
	 	});
	}
}

Dropzone.options.myDropzonePYTHON = { // The camelized version of the ID of the form element
	
	// The configuration we've talked about above
		autoProcessQueue: false, // auto false
		uploadMultiple: true,	// 
		parallelUploads: 10,	// 
		maxFiles: 10,			// 
		maxFilesize: 0.5,
		addRemoveLinks: true,	// Remove 
		acceptedFiles: ".py",		// 

		// The setting up of the dropzone
		// submit-all 
		//	processQueue()
		init: function() {
		var myDropzone = this;
		$("#submit-all").click(function (e) {
			myDropzone.processQueue();
				});
				
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			location.href = parent.document.referrer;
	 	});
	}
}

$('#myTabs a').click(function (e) {
	e.preventDefault()
	$(this).tab('show')
});

jQuery(document).ready(function ($) {
		$('#language').tab();
});

$(document).on('click','.dropdown ul a',function(){
	var className = $(this).attr('class');
	if (!className) {
		var text = $(this).text();
		$(this).closest('.dropdown').children('a.dropdown-toggle').text(text);
		}
	else {
		if (className.substr(className.length-12, 12) != "main-checker") {
			var text = $(this).text();
			$(this).closest('.dropdown').children('a.dropdown-toggle').text(text);
			}
 	}
}); 	

// @@ Show deletion modal
// It shows different contents with modal up to 'target'
function showingDeleteModal(target){
	var items, checkboxes;

	// If target is 'undefined' then, 'toUpperCase' doesn't work.
	// So 'undefinedTab' variable needs.
	var undefinedTab = true; 
	
	if(target == 'college' || target == 'department'){
		items = $('.'+target+'-box-check').length;
		checkboxes = $('.'+target+'-box-check');
		undefinedTab = false;
	}
	else{
		items = $('.box-check').length;
		checkboxes = $('.box-check');
	}

	var cnt = 0;
	for(var i = 0; i < items; i++){
		if(checkboxes[i].checked == true){
			cnt++;
			break;
		}
	}

	if(!undefinedTab){
		target[0] = target.toUpperCase()[0];
	}

	if(cnt == 0){ 
		if(undefinedTab){
			$('#deleteNoItem').modal();
		}
		else{
			$('#deleteNo'+target+'Item').modal();
		}
	}

	else{ 
		if(undefinedTab){
			$('#deleteModal').modal();
		}
		else{
			$('#delete'+target+'Modal').modal();
		}
	}
}

// showing add user modal
function addUserModal(){
	$('#addUserModal').modal();
}

// showing add gruop modal
function addGroupModal(){
	$('#addGroupModal').modal();
}

// @@ Show summary button
// It shows summary button on 'User submission' menu.
// When course administrator clicks on some course, then it shows the button.
// If course administrator stays 'all' tab, then it doesn't show up.
function visibleButton(parent){ 
	var displayOption;
	if(parent.id == "link-all"){
		displayOption = "none";
	}
	else{
		displayOption = "";
	}
	document.getElementById('summary').style.display = displayOption;
}

// @@ Check All checkbox function
// works up to 'Check All' checkbox's checked option
// 'range' means the position of checkboxes.
// it doesn't search in all page range.
function selectAllCheckboxes(range){
	var checkboxes = document.getElementById(range).getElementsByTagName("input");
	var checkAllBox = document.getElementById(range).getElementsByClassName('checkAll')[0];
	// when 'Check All' is unchecked, other checkboxes are being unchecked
	for(var i=0;i<checkboxes.length;i++){
		if(checkboxes[i].type == "checkbox"){
			checkboxes[i].checked = checkAllBox.checked;
		}
	}
}