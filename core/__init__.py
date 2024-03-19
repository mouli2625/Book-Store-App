from flask import Flask



def init_app(database):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']=f'postgresql+psycopg2://postgres:satyamouli@localhost:5432/{database}'
    app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS']=True
    return app



    # db.init_app(app)
    # migrate.init_app(app,db)
    # return app

