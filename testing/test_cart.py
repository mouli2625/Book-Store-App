import pytest
import responses

@pytest.fixture
def book_detail():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp:
        resp = responses.add(
            method=responses.GET,
            url="http://127.0.0.1:7000/getBook?book_id=1",
            json={
                "message":"book_id fetched successfully",
                "book_data":{
                "id":1,
                "title": "nikenduku",
                "author": "lavangam",
                "price": 50,
                "quantity": 10,
                },
                "status":200
            },
            status=200
        )
        return resp
    
import pytest
import responses

@pytest.fixture
def book_detail():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp:
        resp = responses.add(
            method=responses.GET,
            url="http://127.0.0.1:7000/getBook?book_id=1",
            json={
                "message":"book_id fetched successfully",
                "book_data":{
                "id":1,
                "title": "nikenduku",
                "author": "lavangam",
                "price": 50,
                "quantity": 10,
                },
                "status":200
            },
            status=200
        )
        return resp

@responses.activate
def test_user_to_add_cart_should_return_success_response(cart_client, token, book_detail):
    book_data = {
        "bookid": 1,
        "cart_item_quantity": 5
    }
    responses.add(
        method=responses.GET,
        url="http://127.0.0.1:5000/getUser?user_id=1",
        json={
            "message":"User data fetched successfully",
            "status":200, 
            'user_data':{
                "user_id": 1,
                "username": "Mouli",
                "email":"chandramouli3939@gmail.com"
            }
        },
        status=200
    )
    
    response = cart_client.post("/addcart", json=book_data, headers={"Content-Type": "application/json", "Authorization": token})
    print(response.json)
    assert response.status_code == 201

@responses.activate
def test_user_to_add_cart_should_return_failure_response_for_missing_field(cart_client, token, book_detail):
    book_data = {
        "bookid": 1,
        # "cart_item_quantity": 5
    }
    responses.add(
        method=responses.GET,
        url="http://127.0.0.1:5000/getUser?user_id=1",
        json={
            "message":"User data fetched successfully",
            "status":200, 
            'user_data':{
                "user_id": 1,
                "username": "Mouli",
                "email":"chandramouli3939@gmail.com"
            }
        },
        status=200
    )
    
    response = cart_client.post("/addcart", json=book_data, headers={"Content-Type": "application/json", "Authorization": token})
    print(response.json)
    assert response.status_code == 500


@responses.activate
def test_user_for_delete_existing_cart(cart_client, token, book_detail):
    book_data = {
        "bookid": 1,
        "cart_item_quantity": 5
    }
    responses.add(
        method=responses.GET,
        url="http://127.0.0.1:5000/getUser?user_id=1",
        json={
            "message":"User data fetched successfully",
            "status":200, 
            'user_data':{ 
            "user_id": 1,
            "username": "Mouli",
            "email":"chandramouli3939@gmail.com"
            }
        },
        status=200
    )
    
    response = cart_client.post("/addcart", json=book_data, headers={"Content-Type": "application/json", "Authorization":token})
    delete_response = cart_client.delete("/deletecart?cart_id=1", headers={"Content-Type": "application/json", "Authorization":token})
    assert delete_response.status_code == 204

@responses.activate
def test_user_to_order_cart(cart_client, token, book_detail):
    book_data = {
        "bookid": 1,
        "cart_item_quantity": 5
    }
    responses.add(
        method=responses.GET,
        url="http://127.0.0.1:5000/getUser?user_id=1",
        json={
            "message":"User data fetched successfully",
            "status":200, 
            'user_data':{ 
            "user_id": 1,
            "username": "Mouli",
            "email":"chandramouli3939@gmail.com"
            }
        },
        status=200
    )
    responses.add(
        method=responses.PUT,
        url="http://127.0.0.1:7000/updatebooks",
        json={"message":"Book quantity updated successfully","status":200},
        status=200
    )
    
    response = cart_client.post("/addcart", json=book_data, headers={"Content-Type": "application/json", "Authorization":token})
    order_data={
        "cart_id":1
    }
    order_response = cart_client.post("/ordercart",json=order_data,headers={"Content-Type": "application/json", "Authorization":token})
    assert order_response.status_code == 200

@pytest.mark.tyu
@responses.activate
def test_user_to_cancel_ordered_cart(cart_client, token, book_detail):
    book_data = {
        "bookid": 1,
        "cart_item_quantity": 5
    }
    responses.add(
        method=responses.GET,
        url="http://127.0.0.1:5000/getUser?user_id=1",
        json={
            "message":"User data fetched successfully",
            "status":200, 
            'user_data':{ 
            "user_id": 1,
            "username": "Mouli",
            "email":"chandramouli3939@gmail.com"
            }
        },
        status=200
    )
    responses.add(
        method=responses.POST,
        url="http://127.0.0.1:7000/validatebooks",
        json={"message":"All items are ready to order","status":200},
        status=200
    )
    responses.add(
        method=responses.PATCH,
        url="http://127.0.0.1:7000/updatebooks",
        json={"message":"Book quantity updated successfully","status":200},
        status=200
    )
    
    response = cart_client.post("/addcart", json=book_data, headers={"Content-Type": "application/json", "Authorization":token})
    order_data={
        "cart_id":1
    }
    order_response = cart_client.post("/ordercart",json=order_data,headers={"Content-Type": "application/json", "Authorization":token})
    assert order_response.status_code == 200
    delete_order_response = cart_client.delete("/cancelcart?id=1",json=order_data,headers={"Content-Type": "application/json", "Authorization":token})
    assert delete_order_response.status_code == 204


    


