import pytest
import responses

@pytest.fixture
def mock_authentication():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as res:
        res=responses.add(
            method=responses.GET,
            url='http://127.0.0.1:5000/getUser?user_id=1',
            json={"message":"User data fetched successfully",
                  "status":200, 
                  'user_data': {
                    'user_id':1,
                    'username':'Mouli',
                    'password':'Mouli^123',
                    'email':'chandramouli3939@gmail.com',
                    'is_superuser':True,
                    'is_verified':'True'
            }},
        status=201,
        )
        return res

@pytest.fixture
def mock_normal_user_authentication():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as res:
        res=responses.add(
            method=responses.GET,
            url='http://127.0.0.1:5000/getUser?user_id=1',
            json={"message":"User data fetched successfully",
                  "status":200,
                  'user_data': {
                    'user_id':1,
                    'username':'Mouli',
                    'password':'Mouli^123',
                    'email':'chandramouli3939@gmail.com',
                    'is_superuser':False,
                    'is_verified':'True'
            }},
        status=400,
        )
        return res


@responses.activate
def test_superuser_to_add_book_should_return_success_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduku",
        "author":"subbu",
        "price": 30,
        "quantity":5
    }
    
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token})
    assert response.status_code == 201


@responses.activate
def test_normal_user_to_add_book_return_failure_response(book_client,token,mock_normal_user_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 30,
        "quantity":5
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token})
    assert response.status_code == 403

@responses.activate
def test_user_gives_invalid_response_return_failure_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": "jkl",
        "quantity":5
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token})
    assert response.status_code == 400

@responses.activate
def test_user_gives_invalid_quantity_return_failure_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 10,
        "quantity":"hjl"
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token})
    assert response.status_code == 400

@responses.activate
def test_user_to_get_book_return_success_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 10,
        "quantity":20
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token})
    get_response=book_client.get('/getbook',headers={"Content-Type":"application/json","Authorization":token})
    assert get_response.status_code == 200

@responses.activate
def test_user_to_get_book_return_failure_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 10,
        "quantity":20
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token+"a"})
    get_response=book_client.get('/getbook',headers={"Content-Type":"application/json","Authorization":token})
    assert get_response.status_code == 400

@responses.activate
def test_user_to_update_book_return_success_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 10,
        "quantity":20
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token})
    updated_data={
        "title":"nikenduk",
        "author":"lavangam",
        "price": 10,
        "quantity":20
    }
    get_response=book_client.put('/updatebook',json=updated_data,headers={"Content-Type":"application/json","Authorization":token})
    assert get_response.status_code == 200

@responses.activate
def test_user_to_update_book_return_failure_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 10,
        "quantity":20
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token+"a"})
    updated_data={
        "title":"nikenduk",
        "author":"lavangam",
        "price": 10,
        "quantity":20
    }
    get_response=book_client.put('/updatebook',json=updated_data,headers={"Content-Type":"application/json","Authorization":token})
    assert get_response.status_code == 404

@responses.activate
def test_user_to_delete_book_return_success_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 10,
        "quantity":20
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token})
    delete_response=book_client.delete('/deletebook?book_id=1',headers={"Content-Type":"application/json","Authorization":token})
    assert delete_response.status_code == 204

@responses.activate
def test_user_to_delete_book_return_failure_response(book_client,token,mock_authentication):
    data={
        "title":"nikenduk",
        "author":"subbu",
        "price": 10,
        "quantity":20
    }
    response=book_client.post('/addbook',json=data,headers={"Content-Type":"application/json","Authorization":token+"a"})
    delete_response=book_client.delete('/deletebook?book_id=1',headers={"Content-Type":"application/json","Authorization":token})
    assert delete_response.status_code == 404