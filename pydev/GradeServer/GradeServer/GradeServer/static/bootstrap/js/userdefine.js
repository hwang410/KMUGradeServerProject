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
    //  processQueue()
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
    //  processQueue()
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
})

jQuery(document).ready(function ($) {
    $('#language').tab();
})

$(document).on('click','.dropdown ul a',function(){
    var text = $(this).text();
    $(this).closest('.dropdown').children('a.dropdown-toggle').text(text);
}) 	


// showing delete modal
function showingDeleteModal(target){
	var items, checkboxes;
	if(target == 'college'){
		items = $('.college-box-check').length;
		checkboxes = $('.college-box-check');
	}
	else if(target == 'department'){
		items = $('.department-box-check').length;
		checkboxes = $('.department-box-check');
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

	if(cnt == 0){ 
		if(target == 'college'){
			$('#deleteNoCollegeItem').modal();
		}
		else if(target == 'department'){
			$('#deleteNoDepartmentItem').modal();
		}
		else{
	    $('#deleteNoItem').modal();
	  }
  }

	else{ 
		if(target == 'college'){
			$('#deleteCollegeModal').modal();
		}
		else if(target == 'department'){
			$('#deleteDepartmentModal').modal();
		}
		else{
	    $('#deleteModal').modal();
	  }
  }
}

// showing delete modal
function showingEditModal(){
	var items = $('.box-check').length;
	var target = $('.box-check');
	var cnt=0;
	for(var i=0;i<items;i++){
		if(target[i].checked == true){
			cnt++;
			break;
		} 
	}
	if(cnt==0) 
    $('#editNoItem').modal();
  else{
		$('#editModal').modal();
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

function visibleButton(parent){ 
	var thisId = parent.id; 
	//var target = ;
	if(thisId == "link-all"){
		$('#summary').style.display = "none";
	}
	else{
		$('#summary').style.display = "";
	}
}