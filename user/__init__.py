from core import init_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app=init_app("User")
db= SQLAlchemy()
migrate=Migrate()
db.init_app(app)
migrate.init_app(app, db)

