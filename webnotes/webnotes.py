# -*- coding: utf-8 -*-
from flask import Flask, session, request, redirect, url_for, render_template, jsonify, make_response
from werkzeug import SharedDataMiddleware
import random, string, re
from datetime import timedelta, date, datetime
from urllib2 import Request, urlopen, HTTPError
import urllib
import json
from jose import jwt, exceptions, JWTError

app_url = '/sutm/webnotes'
app = Flask(__name__, static_url_path='/sutm/webnotes/static', static_folder='static')
app.secret_key = 'qwe2g7hgfdsazxc1sadadasda321f2f'
app.debug = False #!!!

database = {
	"sutm": {"password": "to-ja", "notes" : [
			{
				"id": 0, "title": "first", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "job", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			},
			{
				"id": 1, "title": "second", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "school", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			},
			{
				"id": 2, "title": "third", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "home", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			}
		], "max-id" : 2}, 
	"bach": {"password": "to-nie-ja", "notes" : [
			{
				"id": 0, "title": "first", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "job", "content" : "Przykład tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			},
                	{
				"id": 1, "title": "second", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "school", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			},
                	{
				"id": 2, "title": "third", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "home", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			}
		], "max-id" : 2},
	"qwe": {"password": "123", "notes" : [
			{
				"id": 0, "title": "first", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "job", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			},
                	{	
				"id": 1, "title": "second", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "school", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			},
                	{	
				"id": 2, "title": "third", "tag" : "-", "creation_date" : datetime.today().strftime("%A %d. %B %Y, %H:%M:%S"),
				"edit_date" : "Nigdy", "category" : "home", "content" : "Przykładowa tresc notatki: a bb ccc dddd eeeee fffff gggggg hhhhhhh"
			}
		], "max-id" : 2}
}

@app.before_request
def func():
        session.modified = True
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
	
@app.route(app_url + '/login', methods=['POST'])
def login():
	claims = request.json
	headers = request.headers
	if 'username' in claims and 'password' in claims:
		if claims['username'] in database and database[claims['username']]["password"] ==  claims["password"]:
			token = jwt.encode(claims, app.secret_key, headers=headers)
			return my_make_response(json.dumps({"token": token}), 200)
		else:
			return my_make_response(json.dumps({'error' : 'User not found!'}), 400)
	else:
		return my_make_response(json.dumps({'error' : '"username" or "password" missing in request!'}), 400)


@app.route(app_url + '/api/notes', methods=['GET'])
def notesGET():
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])
	
	return my_make_response(json.dumps(database[user]['notes']), 200)



@app.route(app_url + '/api/notes', methods=['POST'])
def notesPOST():
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])
	
	body = request.json
	_id = database[user]['max-id'] + 1
	creation_date = datetime.today().strftime("%A %d. %B %Y, %H:%M:%S")
	
	new_note = { #default values
		"id" : _id,
		"title" : "Bez tytułu",
		"tag" : "-",
		"creation_date" : creation_date,
		"edit_date" : "Nigdy",
		"category" : "-",
		"content" : "-"
	}
	if 'title' in body:
		if body['title'] != "":
			new_note['title'] = body['title']
	if 'tag' in body:
		if body['tag'] != "":
			new_note['tag'] = body['tag']
	if 'category' in body:
		if body['category'] != "":
			new_note['category'] = body['category']
	if 'content' in body:
		if body['content'] != "":
			new_note['content'] = body['content']
	
	database[user]['notes'].append(new_note)
	database[user]['max-id'] += 1
	return my_make_response(json.dumps(new_note), 200)

@app.route(app_url + '/api/notes', methods=['DELETE'])
def notesDELETE():
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])
	
	del database[user]['notes']
	database[user]['notes'] = []
	database[user]['max-id'] = -1;
	return my_make_response(json.dumps({"message" : u"Wszystkie notatki usunięte!"}), 200)

@app.route(app_url + '/api/notes/<int:nid>', methods=['GET'])	
def noteGET(nid):
	
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])

	user_note = next((item for item in database[user]['notes'] if item['id'] == nid), None)
	if user_note is None:
                return my_make_response(json.dumps({"error" : "Nie znaleziono notatki o numerze id = " + str(nid)}), 404)
	else:
		return my_make_response(json.dumps(user_note), 200)

@app.route(app_url + '/api/notes/<int:nid>', methods=['DELETE'])
def noteDELETE(nid):
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])
	
	delete_index = None
	for n in range(0,len(database[user]['notes'])):
		if database[user]['notes'][n]['id'] == nid :
			delete_index = n
			break
	if delete_index is None:
		return my_make_response(json.dumps({"error" : "Nie znaleziono notatki o numerze id = " + str(nid) }), 404)
	else:
		del database[user]['notes'][delete_index]
		return my_make_response(json.dumps({"message" : u"Notatka usunięta pomyślnie"}), 200)

@app.route(app_url + '/api/notes/<int:nid>', methods=['PUT'])
def notePUT(nid):
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])
 
	body = request.json
	edited_note = next((item for item in database[user]['notes'] if item['id'] == nid), None)
		
	if edited_note is None:
		return my_make_response(json.dumps({"error" : u"Nie znaleziono notatki o numerze id = " + str(nid)}) ,404)
	
	has_changed = False
	if 'title' in body:
		if body['title'] == "":
			edited_note['title'] = "Bez tytułu"
			has_changed = True
		else:
			edited_note['title'] = body['title']
			has_changed = True
	if 'tag' in body:
		if body['tag'] != "":
			edited_note['tag'] = body['tag']
		else:
			edited_note['tag'] = "-"
		has_changed = True
	if 'category' in body:
		if body['category'] != "":
			edited_note['category'] = body['category']
		else:
			edited_note['category'] = "-"
		has_changed = True
	if 'content' in body:
		if body['content'] == "":
			edited_note['content'] = "-"
		else:
			edited_note['content'] = body['content']
			has_changed = True
	if has_changed:
		edited_note['edit_date'] = datetime.today().strftime("%A %d. %B %Y, %H:%M:%S")
	
	return my_make_response(json.dumps(edited_note), 200)

@app.route(app_url + '/api/categories', methods=['GET'])
@app.route(app_url + '/api/categories/', methods=['GET'])
def categoriesGET():
	check_output = check_token(request)
	if 'user' in check_output['result']:
		user = check_output['result']['user']
	else:
		return my_make_response(json.dumps(check_output['result']), check_output['status_code'])

	categories = []
	for item in database[user]['notes']:
		if item['category'] not in categories:
			categories.append(item['category'])

	return my_make_response(json.dumps(categories), 200)

@app.route(app_url + '/api/tags', methods=['GET'])
@app.route(app_url + '/api/tags/', methods=['GET'])
def tagsGET():
        check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])
        
	tags = []
        for item in database[user]['notes']:
                if item['tag'] not in tags:
                        tags.append(item['tag'])

        return my_make_response(json.dumps(tags), 200)



@app.route(app_url + '/api/categories/<category>', methods=['GET'])
def category_enlist(category):
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])

	notes = []
	for item in database[user]['notes']:
		if item['category'] == category:
			notes.append(item)
	
	if len(notes) == 0:
		return my_make_response(json.dumps({"error": u"Nie znaleziono kategorii: " + category}), 404)
	else:
		return my_make_response(json.dumps(notes), 200)


@app.route(app_url + '/api/tags/<tag>', methods=['GET'])
def tag_enlist(tag):
	check_output = check_token(request)
        if 'user' in check_output['result']:
                user = check_output['result']['user']
        else:
                return my_make_response(json.dumps(check_output['result']), check_output['status_code'])
      	
        notes = []
        for item in database[user]['notes']:
                if item['tag'] == tag:
                        notes.append(item)
	
        if len(notes) == 0:
                return my_make_response(json.dumps({"error":u"Nie znaleziono etykiety: "}), 404)
        else:
                return my_make_response(json.dumps(notes), 200)

#----------------------------------------------

def check_token(request):
	try:
		if 'token' in request.headers: #order of checking matters. Checking headers must be first
			try:
                		if jwt.decode(request.headers['token'], app.secret_key)['username'] in database:
                        		user = jwt.decode(request.headers['token'], app.secret_key)['username']
					result = {"user" : user}
					code = 200
                		else:
                		        result = {'error' : 'Invalid token'}
					code = 401
			except JWTError, e:
				result = {'error' : str(e)}
				code = 401
        	elif 'token' in request.json:
                	if jwt.decode(request.json['token'], app.secret_key)['username'] in database:
                        	user = jwt.decode(request.json['token'], app.secret_key)['username']
				result = {"user" : user}
				code = 200
        	        else:
                	        result = {'error' : 'Invalid token'}
				code = 400
	
        	else:
                	result = {'error' : 'No token in Headers'}
			code = 401
	except TypeError:
		result = {"error" : "token required (checked Headers and Body)."}
		code = 400
		
	return {"status_code" : code, "result" : result}


def my_make_response(resp_body, code):
	resp = make_response(resp_body)
        resp.headers['Content-Length'] = str(len(resp_body))
        resp.headers['Content-Type'] = "application/json"
        resp.headers['Access-Control-Allow-Origin'] = '*'
	resp.status_code = code
        return resp
