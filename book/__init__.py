from core import init_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

app=init_app("Book")
db= SQLAlchemy()
migrate=Migrate()
jwt=JWTManager()
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)