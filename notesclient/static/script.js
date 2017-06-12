hist = new Array();

window.onload = function() {	
	$("#notes_btn").on('click', get_all_notes);
	$("section").on('click','div ul li .note-on-list', show_note);
	$("section").on('mouseenter', 'div ul li', show_buttons);
	$("section").on('mouseleave', 'div ul li', hide_buttons);
	$("#add_btn").on('click', add_note);
	$("#categories_btn").on('click', show_categories);
	$("section").on('click', 'div div div div #category-paragraph', show_category);
	$("#tags_btn").on('click', show_tags);
	$("section").on('click', 'div div div div #tag-paragraph', show_tag);
	$("#button-back").on('click', made_previous_action);
	$("#button-mainpage").on('click', goto_mainpage);
	$("#button-refresh").on('click', refresh);
	$("section").on('click', 'ul .category-reference', show_category);
	$("section").on('click', 'ul .tag-reference', show_tag);
	$("section").on('click', 'div ul li .edit-remove-panel .on-list-delete-btn', delete_note_from_list);
	$("section").on('click', 'div .on-view-delete-btn', delete_note_from_view);
	$("section").on('click', 'div ul li .edit-remove-panel .on-list-edit-btn', edit_note_from_list);
	$("section").on('click', 'div .on-view-edit-btn', edit_note_from_view);
}

function made_previous_action(){
	hist.pop();
	var e = hist.pop();
	
	if(typeof e === 'undefined')
		document.getElementById("content").innerHTML = "";
	else
		$(e.target).trigger('click');
}

function goto_mainpage(event) {
	document.getElementById("content").innerHTML = "";

	var tmp = hist.pop();
        hist.push(tmp);
        if(typeof tmp === 'undefined'){
        	hist.push(event);
        } else if(tmp.target != event.target){
        	hist.push(event);
        }
	$("#current-page-info").text("Strona główna");

}

function refresh() {
	location.reload();
}

function get_all_notes(event) {
	$(this).prepend('<span id="nb-spinner" class="fa fa-spinner fa-fw fa-spin"></span>');
	$.ajax({
		type: "GET",
		url: "http://edi.iem.pw.edu.pl/sutm/notesclient/getNotes",
		dataType: "json",
		success: function(response) {
			render_section_save_history(response, event);

			$(".edit-remove-panel button").hide();
			$("#current-page-info").text("Moje notatki");
			$("#nb-spinner").remove();	
		},
		error: function(response) {
			render_error_info(response);
			$("#nb-spinner").remove();
		}	
	});
}

function show_note(event) {
	var id = this.parentNode.id;
	$.ajax({
		type: 'GET',
		url: "http://edi.iem.pw.edu.pl/sutm/notesclient/getNote/" + id.toString(),
		dataType: "json",
		success:function(response){
			render_section_save_history(response, event);
			
			$("#current-page-info").text("Szczegóły notatki");
		},
		error: function(response) {
                        render_error_info(response);
                }	
	});
}

function add_note(event) {
	$(this).prepend('<span id="ab-spinner" class="fa fa-spinner fa-fw fa-spin"></span>');
	$.ajax({
		type: 'GET',
		url: "http://edi.iem.pw.edu.pl/sutm/notesclient/renderAddNote",
		dataType: "json",
		success: function(response) {
			render_section_save_history(response, event);	

			$("section form div div input[type='radio']").on('change', toggle_category_selection);
                        $("section form div #select-cat select").prop('disabled', true);
                        $("section form div #select-cat span").addClass(" disabled-option ");
			$("#current-page-info").text("Dodawanie notatki");
			$("#ab-spinner").remove();
		},
		error: function(response) {
                        render_error_info(response);
                        $("#ab-spinner").remove();
                }
	});
}

function show_categories(event) {
	$(this).prepend('<span id="cb-spinner" class="fa fa-spinner fa-fw fa-spin"></span>');
	$.ajax({
		type: 'GET',
		url: "http://edi.iem.pw.edu.pl/sutm/notesclient/categories",
		dataType: "json",
		success: function(response) {
			render_section_save_history(response, event);

			$("#current-page-info").text("Kategorie");
			$("#cb-spinner").remove();
		},
		error: function(response) {
                        render_error_info(response);
                        $("#cb-spinner").remove();
                }
	});
}

function show_category(event) {
	var category = this.innerText;
	$(this).prepend("<span id=\""+category+"-spinner\" class='fa fa-spinner fa-fw fa-spin'></span>");
	$.ajax({
		type: 'GET',
		url: 'http://edi.iem.pw.edu.pl/sutm/notesclient/category/' + category,
		dataType: "json",
		success: function(response) {
			render_section_save_history(response, event);
			
			$("#current-page-info").text("Notatki z kategorii: " + category);
			$("#"+category+"-spinner").remove();
		},
		error: function(response) {
                        render_error_info(response);
                }
		
	});
}

function show_tags(event) {
	$(this).prepend('<span id="tb-spinner" class="fa fa-spinner fa-fw fa-spin"></span>');
	$.ajax({
		type: 'GET',
		url: 'http://edi.iem.pw.edu.pl/sutm/notesclient/tags',
		dataType: "json",
		success: function(response) {
			render_section_save_history(response, event);
			
			$("#current-page-info").text("Etykiety");
			$("#tb-spinner").remove();
		},
		error: function(response) {
                        render_error_info(response);
                        $("#tb-spinner").remove();
                }
	});
}

function show_tag(event) {
	var tag = this.innerText;
	$(this).prepend("<span id=\""+tag+"-spinner\" class='fa fa-spinner fa-fw fa-spin'></span>");
	$.ajax({
                type: 'GET',
                url: 'http://edi.iem.pw.edu.pl/sutm/notesclient/tag/' + tag,
                dataType: "json",
                success: function(response) {
			render_section_save_history(response, event);

			$("#current-page-info").text("Notatki z etykietą: " + tag);
			$("#"+tag+"-spinner").remove();
                },
		error: function(response) {
                        render_error_info(response);
                }
        });
}

function edit_note_from_list(event){
	var id = this.parentNode.parentNode.id;
	console.log("form list");
	edit_note(id, event);
}
function edit_note_from_view(event) {
	var id = $("#note-id p").text();
	console.log("from view");
	edit_note(id, event);
}

function edit_note(id, event) {
	$.ajax({
		type: 'GET',
		url: 'http://edi.iem.pw.edu.pl/sutm/notesclient/renderEditNote/' + id,
		dataType: "json",
		success: function(response) {
			render_section_save_history(response, event);
			
			$("#current-page-info").text("Edycja notatki");
			$("section form div div input[type='radio']").on('change', toggle_category_selection);
                        $("section form div #select-cat select").prop('disabled', true);
                        $("section form div #select-cat span").addClass(" disabled-option ");
		},
		error: function(response) {
                        render_error_info(response);
                }
	});
}

function delete_note_from_list() {
	var id = this.parentNode.parentNode.id;
	delete_note(id);
}

function delete_note_from_view(){
	var id = $("#note-id p").text();
	delete_note(id);
}

function delete_note(id){
	
	$.ajax({
		type: 'GET',
		url: 'http://edi.iem.pw.edu.pl/sutm/notesclient/delete/' + id,
		dataType: "json",
		success: function(response) {
			if(response['status'] == "OK" || response['status'] == "API_ERROR") {
                                var section = document.getElementById("content");
                                section.innerHTML = response['html'];
                        } else if(response['status'] == "SESSION_EXPIRED") {
                                window.location.href = response['redirection'];
                        }
			$("#current-page-info").text("Usunięto notatkę");

		},
		error: function(response) {
                        render_error_info(response);
                }
	});
}


function toggle_category_selection() {
	var new_cat_span = $("section form div #new-cat span");
	var new_cat_input = $("section form div #new-cat input[type='text']");
	var select_cat_span = $("section form div #select-cat span"); 
	var select_cat_select = $("section form div #select-cat select");

	if(new_cat_input.prop('disabled')) {
		new_cat_span.removeClass("disabled-option").addClass("enabled-option");
		new_cat_input.prop('disabled', false);
	} else { 
		new_cat_span.removeClass("enabled-option").addClass("disabled-option");
		new_cat_input.prop('disabled', true);
	}

	if(select_cat_select.prop('disabled')) {
		select_cat_span.removeClass("disabled-option").addClass("enabled-option");
		select_cat_select.prop('disabled', false);
	} else { 
		select_cat_span.removeClass("enabled-option").addClass("disabled-option");
		select_cat_select.prop('disabled', true);
	}

}

function show_buttons() {
	$(this).find('.edit-remove-panel button').show();
}
function hide_buttons() {
	$(this).find('.edit-remove-panel button').hide();
}

function render_section_save_history(response, event){
	if(response['status'] == "OK" || response['status'] == "API_ERROR") {
		var section = document.getElementById("content");
		section.innerHTML = response['html'];

		var tmp = hist.pop();
		hist.push(tmp);
		if(typeof tmp === 'undefined') {
			hist.push(event);
		}else if(tmp.target != event.target){
			hist.push(event);
		}
	} else if(response['status'] == "SESSION_EXPIRED") {
		window.location.href = response['redirection'];
	}
}

function render_error_info(response) {
	if(response.status == 502)
		msg = "Nie udało sie połączyć z aplikacją";
	else
		msg = "Nieznany błąd"

	$("#content").html(
	"<div id='info-box'>" +
		"<div id='info-img-red'>" + 
			"<span class='fa fa-times-rectangle fa-3x'> </span>" +
		"</div>" + 
        	"<div id='info-text-red'>" + 
                	"<p> Błąd "+ response.status.toString() +" - " + msg + "</p>" +
        	"</div>" + 
	"</div>"
	);
}

/////////////////////////////////////////////////////////////////////
