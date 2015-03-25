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

// when the score is 100, set 'one more?'
// else set 'try again'
function moveWhereAfterSubmit(score){
	$('#move_after').load(function(){
    	//var buttonContent = document.getElementById("move_after");
    	var score = 100;
    	if(score == 100){
    		//buttonContent.innerHTML = "one more?";
    		this.innerHTML = "one more?";
    	}
    	else{
    		//buttonContent.innerHTML = "try again";
    		this.innerHTML = "try again";
    	}
    });
}

// if score is 100, moving to problem List
// else, moving to back page(problem information)
function letItMove(where){
	var place = where.innerHTML;
	if(place == "one more?"){
		window.location = "../userSignin/problemList";
	}
	else{
		history.back();
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


/*
// set donut chart graph
$.getScript('../../static/bootstrap/js/Chart.js',function(){
	var data = [];
	var options = {
		animation: false
	};

  //Get the context of the canvas element we want to select
  var c = $('#submitChart');
  var ct = c.get(0).getContext('2d');
  var ctx = document.getElementById("submitChart").getContext("2d");
  var colors = new Array("#0c274c", "#18709c", "#19bdc4", "#fff6ee", "#ef4089");
  
  myNewChart = new Chart(ct).Doughnut(data, options);
  // input values and colors into the chart
  // need to change 'value:#' 
  for(var i=0;i<5;i++){
  	myNewChart.addData({
  		value:10,
  		color: colors[i]
  	})
  }
})
        */

// textarea auto resize function
/*$('textarea').bind('keyup keypress', function() {
    $(this).height('');
    var brCount = this.value.split('\n').length;
    this.rows = brCount+1; //++ To remove twitching
    var areaH = this.scrollHeight,
        lineHeight = $(this).css('line-height').replace('px',''),
        calcRows = Math.floor(areaH/lineHeight);
    this.rows = calcRows;
});*/

var textarea = $('#copycode');

ace.config.set("basePath", "../../static/bootstrap/js/src");
var editor = ace.edit("editor");
ace.require("ace/ext/language_tools");
editor.session.setMode("ace/mode/c_cpp");
editor.setTheme("ace/theme/eclipse");
editor.setAutoScrollEditorIntoView(true);
editor.setOption("maxLines", 70);
editor.setOption("minLines", 20);
editor.setOption("showPrintMargin", false);

editor.getSession().on('change', function () {
       textarea.val(editor.getSession().getValue());
   });
// language change
function selectLanguage(selectObj) {
	var mode;
	var theme;
	if(selectObj.value == 1 || selectObj.value == 2){ mode = "c_cpp"; }
	if(selectObj.value == 3){ mode = "java"; }
	if(selectObj.value == 4 || selectObj.value == 5){ mode = "python"; }
	if(selectObj.value == 6){ theme = "ambiance"; }
	if(selectObj.value == 7){ theme = "chaos"; }
	if(selectObj.value == 8){ theme = "chrome"; }
	if(selectObj.value == 9){ theme = "clouds_midnight"; }
	if(selectObj.value == 10){ theme = "clouds"; }
	if(selectObj.value == 11){ theme = "cobalt"; }
	if(selectObj.value == 12){ theme = "crimson_editor"; }
	if(selectObj.value == 13){ theme = "dawn"; }
	if(selectObj.value == 14){ theme = "dreamweaver"; }
	if(selectObj.value == 15){ theme = "eclipse"; }
	if(selectObj.value == 16){ theme = "github"; }
	if(selectObj.value == 17){ theme = "idle_fingers"; }
	if(selectObj.value == 18){ theme = "katzenmilch"; }
	if(selectObj.value == 19){ theme = "kr_theme"; }
	if(selectObj.value == 20){ theme = "kuroir"; }
	if(selectObj.value == 21){ theme = "merbivore_soft"; }
	if(selectObj.value == 22){ theme = "merbivore"; }
	if(selectObj.value == 23){ theme = "mono_industrial"; }
	if(selectObj.value == 24){ theme = "monokai"; }
	if(selectObj.value == 25){ theme = "pastel_on_dark"; }
	if(selectObj.value == 26){ theme = "solarized_dark"; }
	if(selectObj.value == 27){ theme = "solarized_light"; }
	if(selectObj.value == 28){ theme = "terminal"; }
	if(selectObj.value == 29){ theme = "textmate"; }
	if(selectObj.value == 30){ theme = "tomorrow_night_blue"; }
	if(selectObj.value == 31){ theme = "tomorrow_night_bright"; }
	if(selectObj.value == 32){ theme = "tomorrow_night_eighties"; }
	if(selectObj.value == 33){ theme = "tomorrow_night"; }
	if(selectObj.value == 34){ theme = "tomorrow"; }
	if(selectObj.value == 35){ theme = "twilight"; }
	if(selectObj.value == 36){ theme = "vibrant_ink"; }
	if(selectObj.value == 37){ theme = "xcode"; }

		var textarea = $('#copycode');
		
    ace.config.set("basePath", "../static/js/src");
    var editor = ace.edit("editor");
    ace.require("ace/ext/language_tools");
    editor.session.setMode("ace/mode/" + mode);
    editor.setTheme("ace/theme/" + theme);
    editor.setAutoScrollEditorIntoView(true);
    editor.setOption("maxLines", 70);
    editor.setOption("minLines", 20);
    
    editor.getSession().on('change', function () {
       textarea.val(editor.getSession().getValue());
   		});
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
    //  processQueue()
  init: function() {
  	var myDropzone = this;
  	$("#submit-all").click(function (e) {
  		myDropzone.processQueue();
      	});
        
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			address = "http://localhost/problemList/" + response;
			location.href=address;
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
    //  processQueue()
    init: function() {
  	var myDropzone = this;
  	$("#submit-all").click(function (e) {
  		myDropzone.processQueue();
      	});
        
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			address = "http://localhost/problemList/" + response;
			location.href=address;
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
    acceptedFiles: ".java .class, .jar",		// 

    // The setting up of the dropzone
    // submit-all 
    //  processQueue()
    init: function() {
  	var myDropzone = this;
  	$("#submit-all").click(function (e) {
  		myDropzone.processQueue();
      	});
        
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			address = "http://localhost/problemList/" + response;
			location.href=address;
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
    //  processQueue()
    init: function() {
  	var myDropzone = this;
  	$("#submit-all").click(function (e) {
  		myDropzone.processQueue();
      	});
        
		this.on("successmultiple", function(files, response) {
		// Gets triggered when the files have successfully been sent.
		// Redirect user or notify of success
			address = "http://localhost/problemList/" + response;
			location.href=address;
	 	});
	}
}

$('#myTabs a').click(function (e) {
  e.preventDefault()
  $(this).tab('show')
})

jQuery(document).ready(function ($) {
    $('#language').tab();
})

$(document).on('click','.dropdown ul a',function(){
    var text = $(this).text();
    $(this).closest('.dropdown').children('a.dropdown-toggle').text(text);
}) 	


// showing delete modal
function showingDeleteModal(){
	var items = $('.box-check').length;
	var target = document.getElementsByClassName('box-check');
	var cnt=0;
	for(var i=0;i<items;i++){
		if(target[i].checked == true) cnt++;
	}
	if(cnt==0) 
        $('#deleteNoItem').modal();
    else 
        $('#deleteModal').modal();
}
// showing delete modal
function showingEditModal(){
	var items = $('.box-check').length;
	var target = document.getElementsByClassName('box-check');
	var cnt=0;
	for(var i=0;i<items;i++){
		if(target[i].checked == true) cnt++;
	}
	if(cnt==0) 
        $('#editNoItem').modal();
    else 
        $('#editModal').modal();
}

// showing add user modal
function addUserModal(){
	$('#addUserModal').modal();
}

// showing add gruop modal
function addGroupModal(){
	$('#addGroupModal').modal();
}

function visibleButton(parent){ 
	var thisId = parent.id; 
	//var target = ;
	if(thisId == "link-all"){
		document.getElementById('summary').style.display = "none";
	}
	else{
		document.getElementById('summary').style.display = "";
	}
}

/* when server administrator add new users */
function addIndivisualUserForm(permission){
  var targetTable = document.getElementById('indivisual');
  var numOfRow = targetTable.rows.length;

  reset_val = function(){
    if(permission == 'course'){
      $("#courseId1").val("");
    }
    $("#userId1").val("");
    $("#username1").val("");
    $("#authority1").val("");
    $("#college1").val("");
    $("#department1").val("");
  }

  var newRow = targetTable.insertRow(2);
  var uploadObj;
  var keys = ['courseId', 'userId', 'college', 'department', 'username', 'authority'];
  var placeholders = ['Course Id', 'User Id', 'College', 'Department', 'User name', 'Authority'];

  for(var i = 0; i < targetTable.rows[0].cells.length; i++){  
    uploadObj = "<tr><td><input type='text' class='input-small formLine1' ";
    if(permission == 'server'){
      i += 1;
    }
    uploadObj += "id = '" + keys[i] + numOfRow + "' name = '" + keys[i] + numOfRow + "' placeholder = '" + placeholders[i] + "' value = '" + $("#" + keys[i] + "1").val();
    if(permission == 'server'){
      i -= 1;
    }
    newRow.insertCell(i).innerHTML = uploadObj + "' form='addIndivisualUser'></td>";
  }
  reset_val();
}

function manageUserForm(){
  var val_cID;
  var val_uID;
  var m_name,d_name;
  var usertb=document.getElementById('manageusertb');
  
  reset_val = function(){
    val_cID = $("#search-courses").val("");
    val_uID = $("#search-members").val("");
  }

  var newRow = usertb.insertRow(usertb.rows.length);
  
  for(var i = 0; i <usertb.rows[0].cells.length; i++){
    val_cID = $("#search-courses").val();
    val_uID = $("#search-members").val();

    var c= newRow.insertCell(i);
    switch (i){
      case 0:
        var uploadObj = "<td>" + val_cID + "</td>";
        break;
      case 1:
        var uploadObj = "<td>" + val_uID + "</td>";
        break;
      case 2:
        var uploadObj="<td>" + memberName + "</td>";
        break;
      case 3:
        var uploadObj="<td>" + memberDepartments + "</td>";
        break;
    }
    c.innerHTML=uploadObj;   
  } 
  reset_val(); 
}

function resetIndivisualUserForm(){
  document.getElementById("indivisualUserForm").innerHTML = '<tr class="formLine"><td><input type="text" class="input-small formLine1" id="userId1" name="userId1" placeholder="User ID" value="" form="addIndivisualUser"></td><td><input type="text" class="input-small formLine1" id="college1" name="college1" placeholder="College" value="" form="addIndivisualUser"></td><td><input type="text" class="input-small formLine1" id="department1" name="department1" placeholder="Department" value="" form="addIndivisualUser"></td><td><input type="text" class="input-small formLine1" id="username1" name="username1" placeholder="User Name" value="" form="addIndivisualUser"></td><td><input type="text" class="input-small formLine1" id="authority1" name="authority1" placeholder="Authority" value="" form="addIndivisualUser"></td></tr>';
}