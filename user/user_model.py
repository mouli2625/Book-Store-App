from user import db
from passlib.hash import pbkdf2_sha256


class User(db.Model):
    __tablename__='Users'
    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    email=db.Column(db.String(150),nullable=False,unique=False)
    is_superuser=db.Column(db.Boolean, default=False)
    is_verified=db.Column(db.Boolean, default=False)


def verify_password(self, raw_password):
    return pbkdf2_sha256.verify(raw_password, self.password)

    
        

