# -*- coding: utf-8 -*-
from urllib2 import Request, urlopen, HTTPError
from datetime import date
import sys
import argparse
import sqlite3
import json
import readline
def close(conn, code):
        conn.commit()
        conn.close()
        sys.exit(code)


def user_exists(c):
	c.execute("SELECT * FROM logged_user")
    exists = c.fetchone()
	if exists is None:
		return False
	else:
		return True

def show_error(e, replace = True):
	rb= e.read()
	if replace:
        rb = rb.replace("'", "\"")
        data = json.loads(rb)
			
        if 'error' in data:
			print "Error " + str(e.code) + " - " + e.reason + \
                	"\n\n" + data['error'] + "\n"
            close(conn,1)
        else:
			print "Error " + e.code + " - " +  e.reason + "\n"
            close(conn,1)

if __name__ == "__main__":
	app_url = "http://edi.iem.pw.edu.pl/sutm/webnotes"
	
	parser = argparse.ArgumentParser()
	parser.add_argument("--login", help="User's name requires to login to the application ")
	parser.add_argument("--passw", help="User's password required to login to the application")
	parser.add_argument("--user", help="Show which user is acutally logged in", action="store_true")
	parser.add_argument("--logout", help="Sign out logged user", action="store_true")
	parser.add_argument("--getall", help="Lists all notes", action="store_true")
	parser.add_argument("--deleteall", help="Deletes all notes", action="store_true")
	parser.add_argument("--get", help="Shows one note with given ID")
	parser.add_argument("--delete", help="Deletes one note with given ID")
	parser.add_argument("--edit", help="Edits note with given ID")
	parser.add_argument("--add", help="Add new note", action = "store_true")
	parser.add_argument("--categories", help="Lists all categories", action="store_true")
	parser.add_argument("--category", help="Shows all notes from given category")
	parser.add_argument("--tags", help="Lists all tags", action="store_true")
	parser.add_argument("--tag", help="Shows all notes with given tag")
	args = parser.parse_args()
	
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	
	# Create table
	c.execute('''CREATE TABLE IF NOT EXISTS logged_user
             (uname text, token text, lastActivity text)''')

	if args.login is not None and args.passw is not None:
		login_date = date.today().strftime("%A %d. %B %Y")
		if not user_exists(c):
			data = {}
        	data['username'] = args.login
        	data['password'] = args.passw
			json_data = json.dumps(data)
			req = Request("http://edi.iem.pw.edu.pl/sutm/webnotes/login", json_data, headers={"Content-Type" : "application/json"})
			req.get_method = lambda: 'POST'
			try:
				response=urlopen(req)
				response_data=json.load(response)
				if 'token' in response_data:
					c.execute("INSERT INTO logged_user VALUES (?,?,?)", (args.login, response_data['token'], login_date,))
					print "\nWelcome " + args.login +"!. Your token is: \n\n" + response_data['token'] + \
						"\n\nYou don't need to save this token - it's going to be stored until you log out manually.\n"
					close(conn,0)
			except HTTPError, e:
				show_error(e)
		else: 
			print "\nSomeone is already logged. \nUse --user to see who is already logged in\n"
			close(conn, 1)



	if args.user:
		c.execute("SELECT * FROM logged_user")
        exists = c.fetchone()
		if exists is None:
			print "\nNo user logged\n"
			close(conn, 0)
		else:
			print "\nAlready logged user is: " + exists[0] + "\n"
			close(conn, 0)
	
	
	
	if args.logout:
		c.execute("SELECT * FROM logged_user")
		user = c.fetchone()
		if user is not None:
			print "\nUser '" + user[0] + "' has been logged out.\n"
			c.execute("DELETE FROM logged_user")
		else:
			print "\nNo user logged\n"
		close(conn, 0)
	


	if args.getall:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			req = Request(app_url + '/api/notes', headers={"Content-Type" : "application/json", "token" : token})
			req.get_method = lambda: 'GET'
			try:
				response = urlopen(req)
				response_data = json.load(response)
				print ""
				if len(response_data) == 0:
					print "You have 0 notes.\n"
				for item in response_data:
					print "Note ID:".rjust(14), item['id']
					print "Title:".rjust(14), item['title']
					print "Tag:".rjust(14), item['tag']
					print "Category:".rjust(14), item['category']
					print "Content:".rjust(14), item['content']
					print "\n==================================================\n"
				close(conn, 0)
			except HTTPError, e:
				show_error(e)
		else:
			print "\nPlease, sign in to see your notes.\n"
			close(conn, 1)
	


	if args.deleteall:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			req = req = Request(app_url + '/api/notes', headers={"Content-Type" : "application/json", "token" : token})
                        req.get_method = lambda: 'DELETE'
			try:
				response = urlopen(req)
				response_data = json.load(response)
				print "\n" + response_data['message'] + "\n"
				close(conn, 0)
			except HTTPError, e:
				show_error(e)
		else:
			print "\nPlease, sign in to see your notes.\n"
                        close(conn, 1)



	if args.get is not None:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			req = Request(app_url + '/api/notes/' + args.get, headers={"Content-Type" : "application/json", "token" : token})
			req.get_method = lambda: 'GET'
			try:
				response = urlopen(req)
				response_data = json.load(response)
				print "\n==================================================\n"
				print "Note ID:".rjust(14), response_data['id']
                                print "Title:".rjust(14), response_data['title']
                                print "Tag:".rjust(14), response_data['tag']
                                print "Category:".rjust(14), response_data['category']
                                print "Creation date:".rjust(14), response_data['creation_date']
                                print "Modified:".rjust(14), response_data['edit_date']
                                print "Content:".rjust(14),response_data['content']
                                print "\n==================================================\n"
				close(conn, 0)
			except HTTPError, e:
				show_error(e)
		else:
			print "\nPlease, sign in to see your note\n"
			closer(conn, 1)


	
	if args.delete is not None:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			req = Request(app_url + '/api/notes/' + args.delete, headers={"Content-Type" : "application/json", "token" : token})
			req.get_method = lambda: 'DELETE'
			try:
				response = urlopen(req)
				response_data = json.load(response)
				print "\n" + response_data['message'] + "\n"
				close(conn, 0)
			except HTTPError, e:
				show_error(e)
		else:
			print "\nPlease, sign in to delete notes\n"
                        close(conn, 1)


	
	if args.edit is not None:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			req = Request(app_url + '/api/notes/' + args.edit, headers={"Content-Type" : "application/json", "token" : token})
			req.get_method = lambda: 'GET'
			response_data = None
			try:
				response = urlopen(req)
				response_data = json.load(response)
			except HTTPError, e:
				print e.read()
				show_error(e)
			
			
			print "\nIf you want to omit field, type '*' and press ENTER\n"
			print "Previous TITLE:".rjust(19), response_data['title']
			new_title = raw_input("New TITLE:".rjust(19) + " ")
			print "---------------------------"
			print "Prevoius TAG:".rjust(19), response_data['tag']
			new_tag = raw_input("New TAG:".rjust(19) + " ")
			print "---------------------------"
			print "Prevoius CATEGORY:".rjust(19), response_data['category']
                        new_category = raw_input("New CATEGORY:".rjust(19) + " ")
			print "---------------------------"
			print "Prevoius CONTENT:".rjust(19), response_data['content']
			new_content = raw_input("New CONTENT:".rjust(19) + " ")
			print "---------------------------"

			data = {}
			if new_title != '*':
				data['title'] = new_title
			if new_tag != '*':
				data['tag'] = new_tag
			if new_category != '*':
				data['category'] = new_category
			if new_content != '*':
				data['content'] = new_content
			
			json_data = json.dumps(data)
			req.data = json_data
			req.get_method = lambda: 'PUT'
			try:
				response = urlopen(req)
				response_data = json.load(response)
				print "\nNote #" + str(response_data['id']) + " edited!"
				print "\n==================================================\n"
                                print "Note ID:".rjust(14), (response_data['id'])
                                print "Title:".rjust(14), response_data['title']
                                print "Tag:".rjust(14), response_data['tag']
                                print "Category:".rjust(14), response_data['category']
                                print "Creation date:".rjust(14), response_data['creation_date']
                                print "Modified:".rjust(14), response_data['edit_date']
                                print "Content:".rjust(14),response_data['content']
                                print "\n==================================================\n"
                                close(conn, 0)
			except HTTPError, e:
				show_error(e)
		else:
			print "\nPlease, sign in to edit notes\n"
                        close(conn, 1)


	if args.add:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			
                        new_title = raw_input("New TITLE:".rjust(19) + " ")
                        print "---------------------------"
                        new_tag = raw_input("New TAG:".rjust(19) + " ")
                        print "---------------------------"
                        new_category = raw_input("New CATEGORY:".rjust(19) + " ")
                        print "---------------------------"
                        new_content = raw_input("New CONTENT:".rjust(19) + " ")
                        print "---------------------------"

                        data = {}
                        data['title'] = new_title
                        data['tag'] = new_tag
                        data['category'] = new_category
                        data['content'] = new_content

                        json_data = json.dumps(data)
			req = Request(app_url + '/api/notes', json_data, headers={"Content-Type" : "application/json", "token" : token})
                        req.get_method = lambda: 'POST'
                        try:
                                response = urlopen(req)
                                response_data = json.load(response)
                                print "\nNote #" + str(response_data['id']) + " added!"
                                print "\n==================================================\n"
                                print "Note ID:".rjust(14), (response_data['id'])
                                print "Title:".rjust(14), response_data['title']
                                print "Tag:".rjust(14), response_data['tag']
                                print "Category:".rjust(14), response_data['category']
                                print "Creation date:".rjust(14), response_data['creation_date']
                                print "Content:".rjust(14),response_data['content']
                                print "\n==================================================\n"
                                close(conn, 0)
			except HTTPError, e:
				show_error(e)
		else:
			print "\nPlease, sign in to add notes\n"
                        close(conn, 1)


	if args.categories:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			req = Request(app_url + '/api/categories', headers={"Content-Type" : "application/json", "token" : token})
			req.get_method = lambda: 'GET'
			try:
				response = urlopen(req)
				response_data = json.load(response)
				print "\nCategories:\n"
				for category in response_data:
					print category +","
				close(conn, 0)
			except HTTPError, e:
				show_error(e)
		else:
			print "\nPlease, sign in to show categories\n"
			close(conn, 1)


	if args.category is not None:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
			token = c.fetchone()[0]
			req = Request(app_url + '/api/categories/' + args.category, headers={"Content-Type" : "application/json", "token" : token})
			req.get_method = lambda: 'GET'
			try: 
				response = urlopen(req)
				response_data = json.load(response)
				print "\nNotes from \"" + args.category + "\" category:\n"
				for item in response_data:
					print "Note ID:".rjust(14), str(item['id'])
                                        print "Title:".rjust(14), item['title']
                                        print "Tag:".rjust(14), item['tag']
                                        print "Category:".rjust(14), item['category']
                                        print "Content:".rjust(14), item['content']
                                        print "\n==================================================\n"
				close(conn, 0)
			except HTTPError, e:
				show_error(e, replace=False)
		else:
			print "\nPlease, sign in to see notes form this category\n"
                        close(conn, 1)

	
	if args.tags:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
                        token = c.fetchone()[0]
                        req = Request(app_url + '/api/tags', headers={"Content-Type" : "application/json", "token" : token})
                        req.get_method = lambda: 'GET'
                        try:
                                response = urlopen(req)
                                response_data = json.load(response)
                                print "\nTags:\n"
                                for tag in response_data:
                                        print tag +","
                                close(conn, 0)
                        except HTTPError, e:
                                show_error(e, replace=False)
		else:
			print "\nPlease, sign in to see tags.\n"
			close(conn, 1)

	
	if args.tag is not None:
		if user_exists(c):
			c.execute("SELECT token FROM logged_user")
                        token = c.fetchone()[0]
                        req = Request(app_url + '/api/tags/' + args.tag, headers={"Content-Type" : "application/json", "token" : token})
                        req.get_method = lambda: 'GET'
                        try:
                                response = urlopen(req)
                                response_data = json.load(response)
                                print "\nNotes with \"" + args.tag + "\" tag:\n"
                                for item in response_data:
                                        print "Note ID:".rjust(14), str(item['id'])
                                        print "Title:".rjust(14), item['title']
                                        print "Tag:".rjust(14), item['tag']
                                        print "Category:".rjust(14), item['category']
                                        print "Content:".rjust(14), item['content']
                                        print "\n==================================================\n"
                                close(conn, 0)
                        except HTTPError, e:
                                show_error(e, replace=False)
		else:
			print "/nPlease, sign in to see notes with this tag.\n"
			close(conn, 1)
	else:
		print ""
#------------------------------------------

