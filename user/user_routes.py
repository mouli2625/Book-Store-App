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


api=Api(app=app, title='Book Store Api',security='apiKey',
        authorizations={
            'apiKey':{
                'type':'apiKey',
                'in':'header',
                'required':True,
                'name':'Authorization'
            }
        }, 
        doc="/docs")

@api.route('/register','/delete')
class UserApi(Resource):
    
    @api.expect(api.model('signingin',{'username':fields.String(),'email':fields.String(),'password':fields.String(),'superkey':fields.String(required=False)}))
    def post(self):
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
    def delete(self):
        
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
    


@api.route('/login')
class LoginApi(Resource):
    
    @api.expect(api.model('logging in',{'username':fields.String(),'password':fields.String()}))
    def post(self):
        try:
            data=request.get_json()
            user=User.query.filter_by(username=data["username"]).first()
            if user and user.verify_password(data["password"]):
                token=user.token(aud="toLogin",exp=60)
                return {"message":"Logged in successfully","status":200,"token":token},200
            return {"message":"Username or password is incorrect","status":400},400
        except Exception as e:
            return {"message":str(e),"status":500},500
        
    
@api.route('/verify')
class VerifyApi(Resource):
    
    @api.expect(api.model('verifying',{'username':fields.String(),'email':fields.String(),'password':fields.String()}))
    def get(self):
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

@api.route('/forget')
class ForgetPassword(Resource):
    
    @api.expect(api.model('forget',{"email":fields.String()}))
    def post(self):
        try:
            data=request.json
            email=data.get("email")
            user=User.query.filter_by(email=email).first()
            if not user:
                return {"message":"User not found","status":400},400
            token=user.token(aud="forget",exp=15)
            send_mail(user.username,user.email,token)
            return {"message":"Reset mail sent successfully","status":200,"token":token},200
        except Exception as e:
            return {"message":str(e),"status":500},500
        
@api.route('/reset')
class ResetPassword(Resource):

    @api.doc(params={"token":"token for reset password"},body=api.model('reset',{'new_password':fields.String()}))
    def put(self):
        try:
            data=request.json
            new_password=data.get("new_password")
            token=request.args.get("token")
            payload=decode_token(token)
            userid=payload["sub"]
            user=User.query.filter_by(user_id=userid).first()
            if not user:
                return {"message":"User not found","status":400},400
            user.set_password(new_password)
            db.session.commit()
            return {"message":"password reset successfully","status":200},200
        except JWTDecodeError:
            return {"message":"Unable to reset password","status":400},400
        except Exception as e:
            return {"message":str(e),"status":400},400
        

@app.route('/getUser',methods=["GET"])
def get():
        user_id=request.args.get("user_id")
        if not user_id:
            return {"message":"User not found","status":400},400
        user=User.query.get(user_id)
        if not user:
            return {"message":"Invalid User","status":400},400
        return {"message":"User data fetched successfully","status":200, 'data': user.to_json},200



        