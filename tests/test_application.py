#1: Import libraries need for the test
from application.models import Entry, UserData
from datetime import datetime
import pytest
from flask import json

# Unit Test
# Parametrize section contains the data for the test

# Testing of Entry class object
@pytest.mark.parametrize("entrylist",[
    [1, 'sample0.png', '../static/images/sample0.png', 'A'],  
    [2, 'sample1.png', '../static/images/sample1.png', 'B']  
])

def test_EntryClass(entrylist,capsys):
    with capsys.disabled():
        now = datetime.now()
        new_entry = Entry(  userid = entrylist[0],
                            filename = entrylist[1],
                            filepath = entrylist[2],
                            prediction= entrylist[3],  
                            predicted_on= now) 

        assert new_entry.userid == entrylist[0] and type(new_entry.userid) is int
        assert new_entry.filename == entrylist[1] and type(new_entry.filename) is str
        assert new_entry.filepath == entrylist[2] and type(new_entry.filepath) is str
        assert new_entry.prediction == entrylist[3] and type(new_entry.prediction) is str
        assert new_entry.predicted_on == now


# Validity of data entered (Expected failure)
@pytest.mark.xfail
@pytest.mark.parametrize("entrylist", [
    [1, 300, '../static/images/sample0.png', 'A'],  
    [2, 'sample1.png', '../static/images/sample1.png', 20]  
])
def test_EntryValidation(entrylist, capsys):
    test_EntryClass(entrylist, capsys)

# Validity of registration (Range testing)
@pytest.mark.parametrize("entrylist",[
    ['devynchew', 'devynchew@gmail.com', 'password'],  
    ['devynchew1', 'devynchew1@gmail.com', 'password']   
])

def test_UserClass(entrylist,capsys):
    with capsys.disabled():
        new_entry = UserData(  username= entrylist[0], 
                            email = entrylist[1],
                            password = entrylist[2]
                            ) 

        assert new_entry.username == entrylist[0] and len(new_entry.username) >= 4 and len(new_entry.username) <= 15
        assert new_entry.email == entrylist[1] and len(new_entry.email) <= 50
        assert new_entry.password == entrylist[2] and len(new_entry.password) >= 4 and len(new_entry.password) <= 15


# Test add API
@pytest.mark.parametrize("entrylist", [
    [1, 'sample0.png', '../static/images/sample0.png', 'A'],  
    [2, 'sample1.png', '../static/images/sample1.png', 'B']  
])
def test_addAPI(client, entrylist, capsys):
    with capsys.disabled():
        now = datetime.now()
        # prepare the data into a dictionary
        data1 = {'userid': entrylist[0], 
                'filename': entrylist[1],
                'filepath': entrylist[2],
                'prediction': entrylist[3],
                'predicted_on': now
                }
        # use client object  to post
        # data is converted to json
        # posting content is specified
        response = client.post('/api/add',
                               data=json.dumps(data1),
                               content_type="application/json")
        # check the outcome of the action
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body["id"]

# Test get API (by id)
@pytest.mark.parametrize("entrylist", [
    [1, 1, 'sample0.png', '../static/images/sample0.png', 'A'],  
    [2, 2, 'sample1.png', '../static/images/sample1.png', 'B']  
])
def test_getAPI(client, entrylist, capsys):
    with capsys.disabled():
        response = client.get(f'/api/get/{entrylist[0]}')
        ret = json.loads(response.get_data(as_text=True))
        # check the outcome of the action
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        print("Type of response_body: ", type(response_body))
        print("Get entry: ", response_body)


        assert response_body["id"] == entrylist[0]
        assert response_body["userid"] == entrylist[1]
        assert response_body["filename"] == entrylist[2]
        assert response_body["filepath"] == entrylist[3]
        assert response_body["prediction"] == entrylist[4]

# Test get all API
@pytest.mark.parametrize("entrylist", [
        [1, 1, 'sample0.png', '../static/images/sample0.png', 'A'],  
        [2, 2, 'sample1.png', '../static/images/sample1.png', 'B']  
])
def test_getAllAPI(client, entrylist, capsys):
    with capsys.disabled():
        response = client.get(f'/api/getall/{entrylist[0]}')
        ret = json.loads(response.get_data(as_text=True))

        # check the outcome of the action
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        print("Type of response_body: ", type(response_body))
        print("Get all entries: ", response_body)

        assert response_body[0]['userid'] == entrylist[1]

# Test delete API
@pytest.mark.parametrize("id", [1, 2])
def test_deleteAPI(client, id, capsys):
    with capsys.disabled():
        response = client.get(f'/api/delete/{id}')
        ret = json.loads(response.get_data(as_text=True))
        # check the outcome of the action
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body["result"] == "ok"

# Test delete ALL API
@pytest.mark.parametrize("userid", [1, 2])
def test_delete_all_API(client, userid, capsys):
    with capsys.disabled():
        response = client.get(f'/api/delete_all/{userid}')
        ret = json.loads(response.get_data(as_text=True))
        # check the outcome of the action
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body["result"] == "ok"