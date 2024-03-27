from user import db
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token
from datetime import datetime,timedelta


class User(db.Model):
    __tablename__='Users'
    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    email=db.Column(db.String(150),nullable=False,unique=False)
    is_superuser=db.Column(db.Boolean, default=False)
    is_verified=db.Column(db.Boolean, default=False)
    
    
    def __init__(self,username,password,email,**kwargs):
        self.username=username
        self.password=pbkdf2_sha256.hash(password)
        self.email=email
        self.__dict__.update(kwargs)
        
        
    @property    
    def to_json(self):
        return {
            "user_id":self.user_id,
            "username":self.username,
            "email":self.email,
            "is_superuser":self.is_superuser,
            "is_verified":self.is_verified
        }
    
    def verify_password(self, raw_password):
        # print(pbkdf2_sha256.verify(raw_password, self.password))
        return pbkdf2_sha256.verify(raw_password, self.password)
        
        
    def token(self, aud='default', exp=15):
        return create_access_token(identity=self.user_id,
                                additional_claims={'exp':datetime.utcnow()+timedelta(minutes=exp),
                                                    'aud': aud})
    
    def set_password(self,password):
        self.password=pbkdf2_sha256.hash(password)

    
        

