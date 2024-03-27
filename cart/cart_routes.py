from cart import app,db
from flask_restx import Api,Resource,fields
from flask import request
import requests as http
from cart.cart_model import Cart, CartItems
from flask import g
from core.utils import authorize_user
from schemas.cart_validator import Cart_validator
from flask_jwt_extended.exceptions import JWTDecodeError


api=Api(app=app,title='Cart Api',security='apiKey',
        authorizations={
            'apiKey':{
                'type':'apiKey',
                'in':'header',
                'required':True,
                'name':'Authorization'
            }
        }, doc="/docs")

@api.route('/addcart')
class AddingCart(Resource):
    method_decorators=[authorize_user]
    
    @api.doc(headers={"Authorization":"token for adding cart"},
             body=api.model("adding cart",{'bookid':fields.Integer(),'cart_item_quantity':fields.Integer()}))
    
    def post(self):
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
            cart_item.cart_item_price=book_data['data']['price']
            cart.cart_price = sum([item.cart_item_price * item.cart_item_quantity for item in cart.items])
            cart.cart_quantity = sum([item.cart_item_quantity for item in cart.items])
            db.session.commit()
            return {"message":"Cart created successfully","data":cart.to_json,"status":200},200
        except JWTDecodeError as e:
            return {"message":str(e),"status":409},409
        except Exception as e:
            return {"message":str(e),"status":500},500
        

@api.route('/deletecart')

class DeletingCart(Resource):
    method_decorators=[authorize_user]
    @api.doc(headers={"Authorization":"token for deleting cart"},
             body=api.model('Deleting cart',{'cart_id':fields.Integer()}))
    def delete(self,*args,**kwargs):
        try:
            data=request.json
            cartid=data.get('cart_id')
            cart=Cart.query.filter_by(cart_id=cartid).first()
            cart_item=CartItems.query.filter_by(cartid=cartid).first()
            if not cart:
                return {"message":"cart not found","status":400},400
            db.session.delete(cart_item)
            db.session.delete(cart)
            db.session.commit()
            return {"message":"cart deleted successfully","status":204},204
        except Exception as e:
            return {"message":str(e),"status":500},500
        

@api.route('/ordercart','/cancelcart')

class OrderApi(Resource):
    method_decorators=[authorize_user]
    @api.doc(headers={"Authorization":"token for ordering cart"})
    def post(self,*args,**kwargs):
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
            return {"message":str(e),"status":400}
        except Exception as e:
            return {"message":str(e),"status":500}
        
    @api.doc(params={'id':'cart_id that should be cancelled'})
    def delete(self,*args,**kwargs):
        try:
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
            return {"message":str(e),"status":500},500
            
