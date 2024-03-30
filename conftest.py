import pytest
from core import init_app
from user.user_model import db as user_db, User
from book.book_model import db as book_db, Book
from cart.cart_model import db as cart_db, Cart
from user.user_routes import UserApi,LoginApi,VerifyApi,ForgetPassword,ResetPassword
from book.book_routes import AddingBookApi,RetreivingBookApi,DeletingBookApi,UpdatingbookApi
from cart.cart_routes import AddingCart,DeletingCart,OrderApi
from flask_restx import Api

@pytest.fixture

def user_app():
    app=init_app('User','test')
    user_db.init_app(app)
    with app.app_context():
        user_db.create_all()
    api=Api(app)
    api.add_resource(UserApi,'/register','/delete')
    api.add_resource(LoginApi,'/login')
    api.add_resource(VerifyApi,'/verify')
    api.add_resource(ForgetPassword,'/forget')
    api.add_resource(ResetPassword,'/reset')
    # api.add_resource(cart_routes.AddingCart,'/addcart')
    # api.add_resource(cart_routes.DeletingCart,'deletecart')
    # api.add_resource(cart_routes.OrderApi,'/ordercart','/cancelcart')
    yield app
    with app.app_context():
        user_db.drop_all()

@pytest.fixture
def book_app():
    app=init_app('Book','test')
    book_db.init_app(app)
    with app.app_context():
        book_db.create_all()

    api=Api(app)
    api.add_resource(AddingBookApi,'/addbook')
    api.add_resource(RetreivingBookApi,'/getbook')
    api.add_resource(DeletingBookApi,'/deletebook')
    api.add_resource(UpdatingbookApi,'/updatebook')
    yield app
    with app.app_context():
        book_db.drop_all()



@pytest.fixture
def cart_app():
    app=init_app('Cart','test')
    cart_db.init_app(app)
    with app.app_context():
        cart_db.create_all()

    api=Api(app)
    api.add_resource(AddingCart,'/addcart')
    api.add_resource(DeletingCart,'/deletecart')
    api.add_resource(OrderApi,'/ordercart','/cancelcart')
    yield app
    with app.app_context():
        cart_db.drop_all()



@pytest.fixture
def user_client(user_app):
    return user_app.test_client()

@pytest.fixture
def book_client(book_app):
    return book_app.test_client()

@pytest.fixture
def cart_client(cart_app):
    return cart_app.test_client()

@pytest.fixture
def token(user_client,user_app):
    register_data={
        "username":"Mouli",
        "password":"Mouli^123",
        "email":"chandramouli3939@gmail.com",
        "superkey":"Mouli"
    }

    response=user_client.post('/register',json=register_data,headers={"Content-Type":"application/json"})
    login_data={"username":"Mouli","password":"Mouli^123"}
    response=user_client.post('/login',json=login_data,headers={"Content-Type":"application/json"})
    return response.json["token"]
