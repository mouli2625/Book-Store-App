from core import init_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail


app=init_app("User")
db= SQLAlchemy()
migrate=Migrate()
jwt=JWTManager()
mail=Mail()
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
mail.init_app(app)

