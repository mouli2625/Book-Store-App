from user import app,db
from schemas.user_validator import UserValidator
from flask import request
from user.user_model import User,verify_password
from flask import jsonify
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
# from .user_model import verify_password
# @app.route("/") 
# def index():
#     return {}, 200

@app.route('/register',methods=["POST"])
def post():
    try:
        serializer = UserValidator(**request.get_json())
        data=serializer.model_dump()
        data["is_superuser"]=data.pop("superkey")
        user=User(**data)
        db.session.add(user)
        db.session.commit()
        return {"message":"User added successfully","status":201},201
    except Exception as e:
        return {"message":str(e),"status":400},400
    
@app.route('/delete',methods=["DELETE"])
def delete():
    
    data=request.json
    try:
        serializer=UserValidator(username=data['username'],password=data['password'],email=data['email'],superkey=data['superkey'])
        user=User.query.filter_by(username=data['username']).first()
        if user and verify_password(data['password']):
            db.session.delete(user)
            db.session.commit()
            return {"message":"User deleted successfully","status":204},204
        return {"message":"Username or password is incorrect","status":401},401
    except Exception as e:
        return {"message":str(e),"status":400},400


        