import pytest

@pytest.fixture
def superuser():
    return {
        "username":"Rajesh",
        "password":"Rajesh^123",
        "email":"arya1@gmail.com",
        "superkey":"Mouli"
    }

@pytest.fixture
def not_superuser():
    return {
        "username":"Rajesh",
        "password":"Rajesh^123",
        "email":"arya1@gmail.com",
        "superkey":"mouli"
    }

@pytest.fixture
def normaluser():
    return{
        "username":"Chandra",
        "email":"chandramouli3939@gmail.com",
        "password":"Chandra^123",
    }

@pytest.fixture
def invalid_user():
    return{
        "username":"Ch",
        "email":"chandramouli3939@gmail.com",
        "password":"Chandra",
    }

@pytest.fixture
def missing_password_user():
    return{
        "username":"Ch",
        "email":"chandramouli3939@gmail.com",
    }

@pytest.fixture
def missing_username_user():
    return{
        "email":"chandramouli3939@gmail.com",
        "password":"Chandra",
    }


@pytest.fixture
def missing_email_user():
    return{
        "username":"Ch",
        "password":"Chandra",
    }

def test_user_with_correct_superkey_want_success_response(user_client,superuser):
    response=user_client.post('/register',json=superuser,headers={"Content-Type":"application/json"})
    assert response.status_code==201

def test_user_with_wrong_superkey_want_failure_response(user_client,not_superuser):
    response=user_client.post('/register',json=not_superuser,headers={"Content-Type":"application/json"})
    assert response.status_code==400

def test_user_with_no_superkey_want_success_response(user_client,normaluser):
    response=user_client.post('/register',json=normaluser,headers={"Content-Type":"application/json"})
    assert response.status_code==201

def test_user_with_invalid_password_want_failure_response(user_client,invalid_user):
    response=user_client.post('/register',json=invalid_user,headers={"Content-Type":"application/json"})
    assert response.status_code==400

def test_user_with_valid_password_want_success_response(user_client,normaluser):
    response=user_client.post('/register',json=normaluser,headers={"Content-Type":"application/json"})
    assert response.status_code==201

def test_user_with_valid_username_want_success_response(user_client,normaluser):
    response=user_client.post('/register',json=normaluser,headers={"Content-Type":"application/json"})
    assert response.status_code==201

def test_user_with_invalid_username_want_failure_response(user_client,invalid_user):
    response=user_client.post('/register',json=invalid_user,headers={"Content-Type":"application/json"})
    assert response.status_code==400

def test_user_with_missing_password_want_failure_response(user_client,missing_password_user):
    response=user_client.post('/register',json=missing_password_user,headers={"Content-Type":"application/json"})
    assert response.status_code==400

def test_user_with_missing_username_want_failure_response(user_client,missing_username_user):
    response=user_client.post('/register',json=missing_username_user,headers={"Content-Type":"application/json"})
    assert response.status_code==400

def test_user_with_missing_email_want_failure_response(user_client,missing_email_user):
    response=user_client.post('/register',json=missing_email_user,headers={"Content-Type":"application/json"})
    assert response.status_code==400