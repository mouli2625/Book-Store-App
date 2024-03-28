from flask import Flask
from settings import settings
from flask_mail import Mail
from flask_jwt_extended import JWTManager

mail=Mail()
jwt=JWTManager()

def init_app(database,mode="debug"):
    app = Flask(__name__)
    if mode == "debug":
        app.config['SQLALCHEMY_DATABASE_URI']=f'postgresql+psycopg2://postgres:satyamouli@localhost:5432/{database}'
        app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS']=True
        app.config['DEBUG']=True

    if mode == "test":
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///:memory:'
        app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS']=True
        app.config['TESTING']=True
    
    
    app.config['JWT_SECRET_KEY'] = settings.jwt_key
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT']=465
    app.config['MAIL_USE_SSL']= True
    app.config['MAIL_USERNAME']=settings.email_sender
    app.config['MAIL_PASSWORD']=settings.email_password
    mail.init_app(app)
    jwt.init_app(app)
    return app




    # db.init_app(app)
    # migrate.init_app(app,db)
    # return app

