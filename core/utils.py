from flask import request
from flask_jwt_extended.exceptions import JWTDecodeError
from flask_jwt_extended import decode_token
import requests as http
from flask import g


def authorize_user(function):
    def wrapper(*args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return {'message': 'Token not found','status': 404}, 404
            payload = decode_token(token)
            result=payload.get('sub')
            response = http.get(f'http://127.0.0.1:5000/getUser?user_id={result}')
            if response.status_code >= 400:
                return {"message":"Something went wrong","status":401}, 400
            user = response.json()['data']
            g.user = user
            if request.method in ['POST', 'PUT','PATCH']:
                request.json.update(userid=user['user_id'])
            else:
                kwargs.update(user_id=user['user_id'])
        except JWTDecodeError:
            return {'msg': 'Invalid Token','status': 401}, 401
        except Exception as e:
            return {'msg' : str(e), 'status' :500}
        return function(*args, **kwargs)
    wrapper.__name__ == function.__name__
                
    return wrapper