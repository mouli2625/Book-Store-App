from cart import app,db
from flask_restx import Api,Resource,fields
from flask import request
import requests as http
from cart.cart_model import Cart, CartItems
from flask import g
from core.utils import authorize_user
from schemas.cart_validator import Cart_validator
from flask_jwt_extended.exceptions import JWTDecodeError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

api=Api(app=app,title='Cart Api',security='apiKey',
        authorizations={
            'apiKey':{
                'type':'apiKey',
                'in':'header',
                'required':True,
                'name':'Authorization'
            }
        }, doc="/docs")
limiter = Limiter(get_remote_address,app=app,default_limits=["200 per day","50 per day"])

@api.route('/addcart')
class AddingCart(Resource):
    method_decorators=[authorize_user]
    
    @api.doc(headers={"Authorization":"token for adding cart"},
            body=api.model("adding cart",{'bookid':fields.Integer(),'cart_item_quantity':fields.Integer()}))
    @limiter.limit("20 per second")
    def post(self):
        """
    Endpoint for creating a cart.

    This endpoint allows a user to create a cart and add items to it.
    If the authentication token is invalid or missing, it returns an error message with an HTTP status code of 409 (Conflict).
    If an unexpected error occurs during the process, it logs the error and returns an error message
    with an HTTP status code of 500 (Internal Server Error).

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation,
                the cart data, and an HTTP status code.
                Example (success):
                {
                    "message": "Cart created successfully",
                    "data": {...},  # Cart data in JSON format
                    "status": 201
                }

    Raises:
        - 409 Conflict: If the authentication token is invalid or missing.
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
        try:
            serializer=Cart_validator(**request.json)
            data=serializer.model_dump()
            bookid=data['bookid']
            response=http.get(f'http://127.0.0.1:7000/getBook?book_id={bookid}')
            if response.status_code >= 400:
                return {"message": response.json()['message']}
            book_data=response.json()
            userid=g.user['user_id']
            cart=Cart.query.filter_by(userid=userid,is_ordered=False).first()
            if not cart:
                cart=Cart(userid=userid)
                db.session.add(cart)
                db.session.commit()
            price=book_data.get('price',0)
            cart_item = CartItems.query.filter_by(bookid=bookid,cart_item_id=cart.cart_id).first()
            if not cart_item:
                print(cart.cart_id)
                cart_item=CartItems(bookid=bookid, 
                                    cart_item_price=price, 
                                    cart_item_quantity=data['cart_item_quantity'],
                                    cartid=cart.cart_id)
                db.session.add(cart_item)
                db.session.commit()
            cart_item.cart_item_quantity=data['cart_item_quantity']
            cart_item.cart_item_price=book_data['book_data']['price']
            cart.cart_price = sum([item.cart_item_price * item.cart_item_quantity for item in cart.items])
            cart.cart_quantity = sum([item.cart_item_quantity for item in cart.items])
            db.session.commit()
            return {"message":"Cart created successfully","data":cart.to_json,"status":201},201
        except JWTDecodeError as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":409},409
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":500},500
        

@api.route('/deletecart')
class DeletingCart(Resource):

    method_decorators=[authorize_user]

    @api.doc(params={"cart_id":"id of the cart that has to be deleted"},headers={"Authorization":"token for deleting cart"})
    @limiter.limit("20 per second")
    def delete(self,*args,**kwargs):
        """
    Endpoint for deleting a cart.

    This endpoint allows a user to delete a cart along with its associated items.
    If the specified cart ID does not exist, it returns an error message with an HTTP status code of 400 (Bad Request).
    If the cart is deleted successfully, it returns a success message with an HTTP status code of 204 (No Content).
    If an unexpected error occurs during the process, it logs the error and returns an error message
    with an HTTP status code of 500 (Internal Server Error).

    Query Parameters:
        - cart_id (str): The ID of the cart to be deleted.

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation and an HTTP status code.
                Example (success):
                {
                    "message": "Cart deleted successfully",
                    "status": 204
                }
                Example (cart not found):
                {
                    "message": "Cart not found",
                    "status": 400
                }

    Raises:
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
        try:
            cartid=request.args.get("cart_id")
            cart=Cart.query.filter_by(cart_id=cartid).first()
            cart_item=CartItems.query.filter_by(cartid=cartid).first()
            if not cart:
                return {"message":"cart not found","status":400},400
            db.session.delete(cart_item)
            db.session.delete(cart)
            db.session.commit()
            return {"message":"cart deleted successfully","status":204},204
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":500},500
        

@api.route('/ordercart','/cancelcart')

class OrderApi(Resource):
    method_decorators=[authorize_user]
    @api.doc(headers={"Authorization":"token for ordering cart"})
    @limiter.limit("20 per second")
    def post(self,*args,**kwargs):
        """
    Endpoint for ordering a cart.

    This endpoint allows a user to order the items in their cart.
    It validates the availability of books and updates their quantities accordingly.
    If the cart is ordered successfully, it returns a success message with an HTTP status code of 200 (OK).
    If the authentication token is invalid or missing, it returns an error message with an HTTP status code of 400 (Bad Request).
    If an unexpected error occurs during the process, it logs the error and returns an error message
    with an HTTP status code of 500 (Internal Server Error).

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation and an HTTP status code.
                Example (success):
                {
                    "message": "Cart ordered successfully",
                    "status": 200
                }
                Example (unable to validate books):
                {
                    "message": "Unable to validate books",
                    "status": 400
                }

    Raises:
        - 400 Bad Request: If the authentication token is invalid or missing.
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
        try:
            userid=g.user['user_id']
            cart=Cart.query.filter_by(userid=userid).first()
            if not cart:
                return {"message":"cart not found","status":404},404
            items=cart.items
            cart_data={}
            headers={'Content-Type': 'application/json'}
            for item in items:
                cart_data[item.bookid]=item.cart_item_quantity
            validate_response=http.post(f'http://127.0.0.1:7000/validatebooks',
                                        json=cart_data,headers=headers)
            if validate_response.status_code>=400:
                return {"message":"Unable to validate books","status":400},400
            order_response=http.patch(f'http://127.0.0.1:7000/updatebooks',
                                    json=cart_data,headers=headers)
            if order_response.status_code>=400:
                return {"message":"Unable to update books","status":400},400
            cart.is_ordered=True
            db.session.commit()
            return {"message":"cart ordered successfully","status":200},200
        except JWTDecodeError as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":400}
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":500}
        
    @api.doc(params={'id':'cart_id that should be cancelled'},headers={"Authorization":"token for cancelling the cart"})
    @limiter.limit("20 per second")
    def delete(self,*args,**kwargs):
        try:
            """
    Endpoint for cancelling an order.

    This endpoint allows a user to cancel an order by removing the items from the ordered cart and updating
    the book quantities accordingly.
    If the order is cancelled successfully, it returns a success message with an HTTP status code of 204 (No Content).
    If the specified cart ID does not exist or if an error occurs during the process, it returns an error message
    with an HTTP status code of 404 (Not Found) or 500 (Internal Server Error) respectively.

    Query Parameters:
        - id (str): The ID of the cart to cancel the order.

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation and an HTTP status code.
                Example (success):
                {
                    "message": "Order cancelled successfully",
                    "status": 204
                }
                Example (cart not found):
                {
                    "message": "Cart not found",
                    "status": 404
                }

    Raises:
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
            userid=g.user['user_id']
            id=request.args.get('id')
            cart=Cart.query.filter_by(userid=userid,is_ordered=True,cart_id=id).first()
            if not cart:
                return {"message":"cart not found","status":404},404
            items=cart.items
            cart_data={}
            headers={'Content-Type': 'application/json'}
            for item in items:
                cart_data[item.bookid]=-1*item.cart_item_quantity
            order_response=http.patch(f'http://127.0.0.1:7000/updatebooks',
                                    json=cart_data,headers=headers)
            if order_response.status_code>=400:
                return {"message":"Unable to update books","status":400},400
            for items in cart.items:
                db.session.delete(item)
                db.session.commit()
            db.session.delete(cart)
            db.session.commit()
            return {"message":"Order cancelled successfully","status":204},204
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":500},500
            
