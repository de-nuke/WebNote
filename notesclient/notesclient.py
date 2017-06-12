# -*- coding: utf-8 -*-
from flask import Flask, session, request, redirect, url_for, render_template, jsonify
from werkzeug.wrappers import Response
from werkzeug import SharedDataMiddleware
import random, string, re
from datetime import timedelta
from urllib2 import Request, urlopen, HTTPError
import urllib
import json


app_url = '/sutm/notesclient'
app = Flask(__name__, static_url_path='/sutm/notesclient/static', static_folder='static')
app.secret_key = '8k6dj297bnm0q84763mbjgit08vmvajuthdyra47'
app.debug = False #!!!

@app.before_request
def func():
        session.modified = True
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)

@app.route(app_url)
@app.route(app_url + '/')
def main():
	if  'token' in session:
		if 'temp_msg' in session:
			msg = session['temp_msg']
			session.pop('temp_msg')
			return render_template("main.html", msg = msg)
		else:
			return render_template("main.html")
	else:
		return redirect("http://edi.iem.pw.edu.pl/sutm/notesclient/login")

@app.route(app_url + '/login')
@app.route(app_url + '/login/' + '<session_status>')
def login(session_status = ""):
        if 'token' in session:
                return redirect("sutm/notesclient")
        else:
                if(session_status == "sessionExpired"):
                        return  render_template("login.html",
                                        session_exp_msg = u"Twoja sesja wygasła lub nastapiło wylogowanie. Zaloguj sie ponownie, aby móc korzystać z serwisu")
                else:
                        return render_template("login.html")


@app.route(app_url + '/loginCheck', methods=['POST', 'GET'])
def login_check():

        username = request.form['username']
        password = request.form['password']

        data = {}
        data['username'] = username
        data['password'] = password
        json_data = json.dumps(data)

        req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/login", json_data, headers={"Content-Type":"application/json"})
	req.get_method = lambda: 'POST'
        try:
                response = urlopen(req)
                response_data = json.load(response)
                if 'token' in session:
                        if session['token'] == response_data['token']:
                                return redirect(app_url)
                        else:
                                return render_template(
                                        "error_page.html",
                                        error_code = 403,
                                        error_reason = "FORBIDDEN",
					back_location = "/login",
                                        error_info = u"Ktoś inny jest zalogowany na tym komputerze")
                else:
                        session['token'] = response_data['token']
                        return redirect(app_url)
        except HTTPError, e:
                response_body =  e.read()
                response_body = response_body.replace("'", "\"")
		try:
                	data = json.loads(response_body)
		except:
			if e.code == 502:
				data = {'error' : u'Nie udało się połączyć z usługą sieciową'}
			else:
				data = {'error' : u'Nieznany błąd'}

                if 'error' in data:
                        return render_template(
                                "error_page.html",
                                back_location = "/login",
                                error_info = data['error'],
                                error_code = e.code,
                                error_reason = e.reason)
                else:
                        return render_template(
                                "error_page.html",
                                back_location = "/login",
                                error_code = e.code,
                                error_reason = e.reason)


@app.route(app_url + '/logout')
def logout():
        session.clear()
        return redirect("http://edi.iem.pw.edu.pl/sutm/notesclient/login")


@app.route(app_url + '/addNote')
def create():
	if 'token' in session:
		return render_template("new_msg_form.html")
	else:
		return """
			{
				"status" : "SESSION_EXPIRED",
				"redirection" : "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
			} """

@app.route(app_url + '/sendNote', methods=['POST'])
def send():
	if 'token' in session:
		title = request.form['title-input']
		tag = request.form['tag-input']
		content = request.form['content']
		if request.form['category-option'] == "new":
			category = request.form['new_category_text']
		elif request.form['category-option'] == "existing":
			category = request.form['cat-select']
		else:
			category = ""	
		data = {
			"title" : title.strip(),
			"tag" : tag.strip(),
			"category" : category.strip(),
			"content": content.strip()
		}
		
		json_data = json.dumps(data)

		headers= {
			"token": session['token'],
			"Content-Type": "application/json"
		}
		req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/notes", json_data, headers=headers)
		req.get_method = lambda: 'POST'
		try:
			urlopen(req)
			session['temp_msg'] = u"Notatka dodana!"
			return redirect(url_for("main"))
		except HTTPError, e:
			response_body =  e.read()
                        response_body = response_body.replace("'", "\"")

                        try:
        	                data = json.loads(response_body)
	                except:
                	        if e.code == 502:
                        	        data = {'error' : u'Nie udało się połączyć z usługą sieciową'}
                       		else:
                                	data = {'error' : u'Nieznany błąd'}

                        if 'error' in data:
                                return render_template("error_page.html", back_location = "/", error_info = data['error'], error_code = e.code, 
					error_reason = e.reason)
                                     
                        else:
                                return render_template("error_page.html", back_location = "/", error_code = e.code, error_reason = e.reason)
                                       	
	else:
		return render_template("error_page.html",
					back_location = "",
					error_info = u"Tworzenie notatki dostępne tylko dla zalogowanych użytkowników. Prawdopodobnie, twoja sesja wygasła.",
					error_code = 401,
					error_reason = u"UNAUTHORIZED")

@app.route(app_url + '/getNotes', methods=['GET'])
def getnotes():
	if 'token' in session:
		
		req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/notes", headers={"Content-Type": "application/json", "token" : session['token']})
		req.get_method = lambda: 'GET'
		try:
			response = urlopen(req)
			response_data = json.load(response)
			notes_list = list(reversed(response_data))
			for n in notes_list:
				if len(n['content']) > 110:
					n['content'] = n['content'][:82]
					n['content'] += u"... <em>[zobacz więcej]</em>"
			data = {
				"status" : "OK",
				"html" : render_template("all_notes.html", notes_list = notes_list)
			}
			return json.dumps(data)
		except HTTPError, e:
			return show_error(e)
	else:
		return json.dumps({
                        "status" : "SESSION_EXPIRED",
                        "redirection" : "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
                })


@app.route(app_url + '/getNote/' + '<int:nid>', methods=['GET'])
def getnote(nid):
	if 'token' in session:
		req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/notes/"+str(nid),headers={"Content-Type":"application/json","token":session['token']})
		req.get_method = lambda: 'GET'
		try:
			response = urlopen(req)
			response_data = json.load(response)
			data = {
				"status" : "OK",
				"html" : render_template("note.html", note_data=response_data)
			}
			return json.dumps(data)
		except HTTPError, e:
			return show_error(e)
	else:
		return json.dumps({
                        "status" : "SESSION_EXPIRED",
                        "redirection" : "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
                })

@app.route(app_url + '/categories', methods=['GET'])
def categories():
	if 'token' in session:
		req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/categories", headers={"Content-Type":"application/json","token":session['token']})
		req.get_method = lambda: 'GET'
		try:
			response = urlopen(req)
			response_data = json.load(response)

			data = {
				"status" : "OK",
				"html" : render_template("categories.html", categories = response_data)
			}
			return json.dumps(data)
		except HTTPError, e:
			return show_error(e)
	else:
		return json.dumps({
                        "status" : "SESSION_EXPIRED",
                        "redirection" : "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
                })

@app.route(app_url + '/category/<category>', methods=['GET'])
def category(category):
	if 'token' in session:
		req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/categories/" + category,
			headers={"Content-Type" : "application/json", 'token' : session['token']})
		req.get_method = lambda: 'GET'
		try:
			response = urlopen(req)
			response_data = json.load(response)
			notes_list = list(reversed(response_data))
			for n in notes_list:
                                if len(n['content']) > 110:
                                        n['content'] = n['content'][:82]
                                        n['content'] += u"... <em>[zobacz więcej]</em>"
			
			return json.dumps({
				"status" : "OK",
				"html" : render_template("all_notes.html", notes_list = notes_list)
			})
		except HTTPError, e:
			show_error(e)
	else:
		return json.dumps({
			"status" : "SESSION_EXPIRED",
			"redirection": "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
		})	


@app.route(app_url + '/tags', methods=['GET'])
def tags():
        if 'token' in session:
                req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/tags", headers={"Content-Type":"application/json","token":session['token']})
                req.get_method = lambda: 'GET'
                try:
                        response = urlopen(req)
                        response_data = json.load(response)
			
			data = {
				"status" : "OK",
                        	"html" : render_template("tags.html", tags = response_data)
			}
			return json.dumps(data)

                except HTTPError, e:
                        return show_error(e)
        else:
                return json.dumps({
                        "status" : "SESSION_EXPIRED",
                        "redirection" : "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
                })
@app.route(app_url + '/tag/<tag>')
def tag(tag):
	if 'token' in session:
                req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/tags/" + tag,
                        headers={"Content-Type" : "application/json", 'token' : session['token']})
                req.get_method = lambda: 'GET'
                try:
                        response = urlopen(req)
                        response_data = json.load(response)
                        notes_list = list(reversed(response_data))
			for n in notes_list:
                                if len(n['content']) > 110:
                                        n['content'] = n['content'][:82]
                                        n['content'] += u"... <em>[zobacz więcej]</em>"
			
                        return json.dumps({
                                "status" : "OK",
                                "html" : render_template("all_notes.html", notes_list = notes_list)
                        })
                except HTTPError, e:
                        show_error(e)
        else:
                return json.dumps({
                        "status" : "SESSION_EXPIRED",
                        "redirection": "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
                })

	
@app.route(app_url + '/renderAddNote', methods=['GET'])
def renderAddNote():
		if 'token' in session:
			r=Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/categories",headers={"Content-Type":"application/json","token":session['token']})
			r.get_method = lambda: 'GET'
			try:
				response = urlopen(r)
				response_data = json.load(response)	
				return json.dumps({
					"status" : "OK",
					"html" : render_template("add_note.html", category_list = response_data)
				})
			except HTTPError, e:
				show_error(e, back_location="/")
		else:
			return json.dumps({
				"status" : "SESSION_EXPIRED",
				"html" : "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired" 	
			})

@app.route(app_url + '/delete/<int:nid>')
def delete(nid):
	if 'token' in session:
		req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/notes/"+str(nid),headers={"Content-Type":"application/json",'token':session['token']})
		req.get_method = lambda: 'DELETE'
		try:
			response = urlopen(req)
			response_data = json.load(response)
			return json.dumps({
				"status" : "OK",
				"html" : render_template("info_green.html", msg = response_data['message'])
			})
		except HTTPError, e:
			return e.read();
	else:
		return json.dumps({
			"status" : "SESSION_EXPIRED",
			"redirection" : "http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
		})

@app.route(app_url + '/renderEditNote/<int:nid>')
def renderEditNote(nid):
	if 'token' in session:
		req1 = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/notes/"+str(nid),headers={"Content-Type":"application/json",'token':session['token']})
		req1.get_method = lambda: 'GET'
		req2 = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/categories",headers={"Content-Type":"application/json", "token" : session['token']})
		req2.get_method = lambda: 'GET'
		try:
			response1 = urlopen(req1)
			response_data1 = json.load(response1)
			
			response2 = urlopen(req2)
			response_data2 = json.load(response2)
			
			return json.dumps({
				"status" : "OK",
				"html" : render_template("edit_note.html", note_data = response_data1, categories = response_data2)
			})
		except HTTPError, e:
			show_error(e)
			
	else:
		return json.dumps({
			"status" : "SESSION_EXPIRED",
			"redirection":"http://edi.iem.pw.edu.pl/sutm/notesclient/login/sessionExpired"
		})
	
@app.route(app_url + '/sendEditedNote/<int:nid>', methods=['POST'])
def sendEditedNote(nid):
	if 'token' in session:
		title = request.form['title-input']
                tag = request.form['tag-input']
                content = request.form['content']
                if request.form['category-option'] == "new":
                        category = request.form['new_category_text']
                elif request.form['category-option'] == "existing":
                        category = request.form['cat-select']
                else:
                        category = ""
                data = {
                        "title" : title.strip(),
                        "tag" : tag.strip(),
                        "category" : category.strip(),
                        "content": content.strip()
                }

                json_data = json.dumps(data)

                headers= {
                        "token": session['token'],
                        "Content-Type": "application/json"
                }
                req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/api/notes/" + str(nid), json_data, headers=headers)
                req.get_method = lambda: 'PUT'
                try:
                        urlopen(req)
			session['temp_msg'] = u"Notatka zapisana!"
			return redirect(url_for("main"))
                except HTTPError, e:
			response_body =  e.read()
                        response_body = response_body.replace("'", "\"")

                        try:
	                        data = json.loads(response_body)
	                except:
        	                if e.code == 502:
                	                data = {'error' : u'Nie udało się połączyć z usługą sieciową'}
                	        else:
                        	        data = {'error' : u'Nieznany błąd'}

                        if 'error' in data:
                                return render_template("error_page.html", back_location = "/", error_info = data['error'], error_code = e.code,
                                        error_reason = e.reason)

                        else:
                                return render_template("error_page.html", back_location = "/", error_code = e.code, error_reason = e.reason)
	else:
		return render_template("error_page.html",
                                        back_location = "",
                                        error_info = u"Tworzenie notatki dostępne tylko dla zalogowanych użytkowników. Prawdopodobnie, twoja sesja wygasła.",
                                        error_code = 401,
                                        error_reason = u"UNAUTHORIZED")

#------------------------------------------------------------------------------------- 
def show_error(e, status_msg = "API_ERROR", back_location = "/login" ):
	response_body =  e.read()
	print response_body
        response_body = response_body.replace("'", "\"")
        try:
		data = json.loads(response_body)
	except:
		if e.code == 502:
			data = { 'error' : u"Wystąpił błąd usługi sieciowej" }
		else:
			data = {'error' : u"Nieznany błąd"}
	
        if 'error' in data:
		return json.dumps({
			"status" : status_msg,
			"html" : render_template(
			"error_page.html",
			back_location = back_location,
                        error_info = data['error'],
                        error_code = e.code,
                        error_reason = e.reason)
		})
	else:
		return json.dumps({
                	"status" : status_msg,
                	"html" : render_template(
                	"error_page.html",
                	back_location = back_location,
                	error_code = e.code,
                	error_reason = e.reason)
		})
