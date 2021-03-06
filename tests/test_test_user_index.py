import pytest
from flask import g, session
from flaskr.db import get_db
from flaskr.test_user_index import getReport, changeInfectedUser

def test_get_report(app):
	with app.app_context():
		assert getReport("eringwood0") == 0
		changeInfectedUser("adooney21")
		assert getReport("eringwood0") > 0

def test_homepage(client, auth):
	response = client.get('/user_index')
	assert b'auth/login' in response.data

	auth.login('other', 'test')
	response = client.get('/user_index')
	assert b'USER MENU' in response.data

	auth.login('test', 'test')
	response = client.get('/user_index')
	assert b'Admin Menu' in response.data



def test_add_contact_event(client, auth, app):
	username = 'other'
	password = 'test'

	auth.login(username, password)
	response = client.post('/user_index', data={'location':'Safeway', 'time':'00:00'})
	assert b"haven't had contact" in response.data

	with app.app_context():
		changeInfectedUser('adooney21')
		response = client.post('/user_index', data={'location':'Safeway', 'time':'23:00'})
		assert b"you had contact with your fellow users" in response.data
		query = get_db().execute(
			"SELECT * FROM UserLocation WHERE username = 'other'"
			).fetchone()
		assert query is not None

def test_admin_infect(client, auth, app):
	username = 'test'
	password = 'test'

	response = client.get('/user_index_infect')
	assert b'auth/login' in response.data

	auth.login(username, password)
	response = client.get('/user_index_infect')
	assert b'change the infections status' in response.data

	client.post('/user_index_infect', data={'user':'adooney21'})

	with app.app_context():
		query = get_db().execute(
			"select * from Users where username = 'adooney21'"
		).fetchone()
		assert query[4] == 1

def test_admin_change_prob(client, auth, app):
	username = 'test'
	password = 'test'

	response = client.get('/user_index_change_prob')
	assert b'auth/login' in response.data

	auth.login(username, password)
	response = client.get('/user_index_change_prob')
	assert b'change the probability of infection' in response.data

	client.post('/user_index_change_prob', data={'location':'Safeway', 'prob':'99'})

	with app.app_context():
		query = get_db().execute(
			"select * from Location where name = 'Safeway'"
		).fetchone()
		assert query[2] == 0.99