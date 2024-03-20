from user import app,db
from schemas.user_validator import UserValidator
from flask import request
from user.user_model import User
from flask import jsonify
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions  import JWTDecodeError
from user.utils import send_mail
from flask_restx import Api, Resource, fields
from core import init_app
# from .user_model import verify_password
# @app.route("/")
# def index():
#     return {}, 200
app=init_app(database="User")

api=Api(app=app, title='Book Store Api',prefix='/api',security='apiKey',doc="/docs")

@app.route('/register',methods=["POST"])
class UserApi(Resource):
    
    @api.expect(api.model('signingin',{'username':fields.String(),'email':fields.String(),'password':fields.String()}))
    def post():
        try:
            serializer = UserValidator(**request.get_json())
            data=serializer.model_dump()
            data["is_superuser"]=data.pop("superkey")
            user=User(**data)
            # user.is_superuser=True
            db.session.add(user)
            db.session.commit()
            token=user.token("toregister",30)
            send_mail(user.username,user.email,token)
            return {"message":"User added successfully","status":201,"token":token},201
        except Exception as e:
            return {"message":str(e),"status":400},400
    
    # @app.route('/register/delete',methods=["DELETE"])
    @api.expect(api.model('Deleting',{'username':fields.String(),'email':fields.String(),'password':fields.String()}))
    def delete():
        
        data=request.json
        try:
            serializer=UserValidator(username=data['username'],password=data['password'],email=data['email'],superkey=data['superkey'])
            user=User.query.filter_by(username=data['username']).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                return {"message":"User deleted successfully","status":204},204
            return {"message":"Username is incorrect","status":401},401
        except Exception as e:
            return {"message":str(e),"status":400},400
    

@app.route('/login')
def loginpost():
    try:
        data=request.get_json()
        user=User.query.filter_by(username=data["username"]).first()
        if user and user.verify_password(data["password"]):
            token=user.token(aud="toLogin",exp=60)
            return {"message":"Logged in successfully","status":200,"token":token},200
        return {"message":"Username or password is incorrect","status":400},400
    except Exception as e:
        return {"message":str(e),"status":500},500
    
@app.route('/verify')
def verify():
    try:
        token=request.args.get('token')
        if not token:
            return {"message":"Incorrect token","status":404},404
        payload=decode_token(token)
        userid=payload["sub"]
        user=User.query.filter_by(user_id=userid).first()
        if not user:
            return {"message":"User not found","status":404},404
        if user.is_verified:
            return {"message":"User already verified","status":404},404
        user.is_verified=True
        db.session.commit()
        return {"message":"User verified Successfully","status":200},200
    except JWTDecodeError:
        return {"message":"Unable to decode token","status":400},400
    except Exception as e:
        print(e)
        return {"message":str(e),"status":400},400



        