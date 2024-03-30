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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging



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
limiter = Limiter(get_remote_address,app=app,default_limits=["200 per day","50 per day"])

@api.route('/register','/delete')
class UserApi(Resource):
    

    @api.expect(api.model('signingin',{'username':fields.String(),
                                        'email':fields.String(),
                                        'password':fields.String(),
                                        'superkey':fields.String(required=False)}))
    @limiter.limit("20 per second")
    def post(self):
        """
    Endpoint for user registration.

    This endpoint registers a new user by accepting a POST request with JSON data containing user information.
    If registration is successful, it returns a success message along with an authentication token.
    If an error occurs during registration, it returns an error message along with an appropriate HTTP status code.

    Request Body:
        - username (str): The username of the user to be registered.
        - email (str): The email address of the user to be registered.
        - password (str): The password of the user to be registered.
        - superkey (str, optional): An optional superkey for superuser privileges.

    Returns:
        - dict: A dictionary containing a message indicating the result of the registration,
                an HTTP status code, and an authentication token (if registration is successful).
                Example:
                {
                    "message": "User added successfully",
                    "status": 201,
                    "token": "<authentication_token>"
                }

    Raises:
        - 400 Bad Request: If the request body is missing or invalid.
        - 500 Internal Server Error: If an unexpected error occurs during registration.
    """
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
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":400},400
    
    # @app.route('/register/delete',methods=["DELETE"])
    @api.expect(api.model('Deleting',{'username':fields.String(),
                                        'email':fields.String(),
                                        'password':fields.String(),
                                        'superkey':fields.String()}))
    @limiter.limit("20 per second")
    def delete(self):
        """
    Endpoint for deleting a user.

    This endpoint deletes a user by accepting a DELETE request with JSON data containing user information.
    If the specified user exists, it is deleted from the database.
    If deletion is successful, it returns a success message with an HTTP status code of 204 (No Content).
    If the specified user does not exist, it returns an error message with an HTTP status code of 401 (Unauthorized).
    If an error occurs during deletion, it returns an error message with an HTTP status code of 400 (Bad Request).

    Request Body:
        - username (str): The username of the user to be deleted.
        - email (str): The email address of the user to be deleted.
        - password (str): The password of the user to be deleted.
        - superkey (str, optional): An optional superkey for user identification.

    Returns:
        - dict: A dictionary containing a message indicating the result of the deletion and an HTTP status code.
                Example (success):
                {
                    "message": "User deleted successfully",
                    "status": 204
                }
                Example (username incorrect):
                {
                    "message": "Username is incorrect",
                    "status": 401
                }

    Raises:
        - 400 Bad Request: If the request body is missing or invalid.
        - 401 Unauthorized: If the specified username does not exist.
        - 500 Internal Server Error: If an unexpected error occurs during deletion.
    """
        data=request.json
        try:
            serializer=UserValidator(username=data['username'],
                                        password=data['password'],
                                        email=data['email'],
                                        superkey=data['superkey'])
            user=User.query.filter_by(username=data['username']).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                return {"message":"User deleted successfully","status":204},204
            return {"message":"Username is incorrect","status":401},401
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":400},400
    


@api.route('/login')
class LoginApi(Resource):
    
    @api.expect(api.model('logging in',{'username':fields.String(),'password':fields.String()}))
    @limiter.limit("20 per second")
    def post(self):
        """
    Endpoint for user login.

    This endpoint authenticates a user by accepting a POST request with JSON data containing the username and password.
    If the provided credentials are correct, it generates an authentication token for the user.
    If login is successful, it returns a success message along with an authentication token and an HTTP status code of 200 (OK).
    If the provided username or password is incorrect, it returns an error message with an HTTP status code of 400 (Bad Request).
    If an unexpected error occurs during login, it returns an error message with an HTTP status code of 500 (Internal Server Error).

    Request Body:
        - username (str): The username of the user attempting to log in.
        - password (str): The password of the user attempting to log in.

    Returns:
        - dict: A dictionary containing a message indicating the result of the login,
                an HTTP status code, and an authentication token (if login is successful).
                Example (success):
                {
                    "message": "Logged in successfully",
                    "status": 200,
                    "token": "<authentication_token>"
                }
                Example (incorrect username or password):
                {
                    "message": "Username or password is incorrect",
                    "status": 400
                }

    Raises:
        - 400 Bad Request: If the request body is missing or invalid.
        - 500 Internal Server Error: If an unexpected error occurs during login.
    """
        try:
            data=request.get_json()
            user=User.query.filter_by(username=data["username"]).first()
            if user and user.verify_password(data["password"]):
                token=user.token(aud="toLogin",exp=60)
                return {"message":"Logged in successfully","status":200,"token":token},200
            return {"message":"Username or password is incorrect","status":400},400
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":500},500
        
    
@api.route('/verify')
class VerifyApi(Resource):
    
    @api.doc(headers={"Authorization":"token for verifying"})
    @limiter.limit("20 per second")
    def get(self):
        """
    Endpoint for verifying a user.

    This endpoint verifies a user's account based on the provided authentication token.
    If the token is valid and corresponds to an existing user, and the user is not already verified,
    it updates the user's verification status to True.
    If verification is successful, it returns a success message with an HTTP status code of 200 (OK).
    If the token is missing, incorrect, or unable to decode, it returns an error message with an HTTP status code of 400 (Bad Request).
    If the user corresponding to the token is not found or is already verified, it returns an error message with an HTTP status code of 404 (Not Found).

    Query Parameters:
        - token (str): The authentication token associated with the user to be verified.

    Returns:
        - dict: A dictionary containing a message indicating the result of the verification and an HTTP status code.
                Example (success):
                {
                    "message": "User verified Successfully",
                    "status": 200
                }
                Example (incorrect token):
                {
                    "message": "Incorrect token",
                    "status": 404
                }

    Raises:
        - 400 Bad Request: If the token is missing, incorrect, or unable to decode.
        - 404 Not Found: If the user corresponding to the token is not found or is already verified.
    """
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
        except JWTDecodeError as e:
            app.logger.exception(e,exc_info=False)
            return {"message":"Unable to decode token","status":400},400
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":400},400

@api.route('/forget')
class ForgetPassword(Resource):
    
    @api.expect(api.model('forget',{"email":fields.String()}))
    @limiter.limit("20 per second")
    def post(self):
        """
    Endpoint for sending a password reset email.

    This endpoint sends a password reset email to the user associated with the provided email address.
    If the email address corresponds to an existing user, it generates a token for resetting the password,
    sends a reset email containing the token, and returns a success message with an HTTP status code of 200 (OK).
    If no user is found with the provided email address, it returns an error message with an HTTP status code of 400 (Bad Request).
    If an unexpected error occurs during the process, it logs the error and returns an error message with an HTTP status code of 500 (Internal Server Error).

    Request Body:
        - email (str): The email address of the user for which the password reset email should be sent.

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation,
                an HTTP status code, and a password reset token (if applicable).
                Example (success):
                {
                    "message": "Reset mail sent successfully",
                    "status": 200,
                    "token": "<reset_token>"
                }
                Example (user not found):
                {
                    "message": "User not found",
                    "status": 400
                }

    Raises:
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
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
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":500},500
        
@api.route('/reset')
class ResetPassword(Resource):

    @api.doc(params={"token":"token for reset password"},
                body=api.model('reset',{'new_password':fields.String()}))
    
    @limiter.limit("20 per second")
    def put(self):
        """
    Endpoint for resetting a user's password.

    This endpoint resets a user's password based on the provided authentication token and new password.
    If the token is valid and corresponds to an existing user, the user's password is updated with the new password.
    If password reset is successful, it returns a success message with an HTTP status code of 200 (OK).
    If the token is missing, incorrect, or unable to decode, it returns an error message with an HTTP status code of 400 (Bad Request).
    If the user corresponding to the token is not found, it returns an error message with an HTTP status code of 400 (Bad Request).

    Request Body:
        - new_password (str): The new password to be set for the user.

    Query Parameters:
        - token (str): The authentication token associated with the user for password reset.

    Returns:
        - dict: A dictionary containing a message indicating the result of the password reset and an HTTP status code.
                Example (success):
                {
                    "message": "Password reset successfully",
                    "status": 200
                }
                Example (unable to reset password due to token decoding error):
                {
                    "message": "Unable to reset password",
                    "status": 400
                }

    Raises:
        - 400 Bad Request: If the token is missing, incorrect, or unable to decode, or if the user is not found.
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
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
        except JWTDecodeError as e:
            app.logger.exception(e,exc_info=False)
            return {"message":"Unable to reset password","status":400},400
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":400},400
        

@app.route('/getUser',methods=["GET"])
def get():
        user_id=request.args.get("user_id")
        if not user_id:
            return {"message":"User not found","status":400},400
        user=User.query.get(user_id)
        if not user:
            return {"message":"Invalid User","status":400},400
        return {"message":"User data fetched successfully","status":200, 'user_data': user.to_json},200



        