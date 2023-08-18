import os
from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from resources import *
from flask_cors import CORS
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_jwt_extended import JWTManager


app = None
security= None
secret_key = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    secret_key = app.config["JWT_SECRET_KEY"] 
    jwt = JWTManager(app)
    db.init_app(app)
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)
    app.app_context().push()
    return app , security

app, security = create_app()
CORS(app)
api.init_app(app)


# Import all the controllers so they are loaded
from application.controllers import *



if __name__ == '__main__':
  # Run the Flask app
  db.create_all()
  login_manager.init_app(app)
  app.run(host='0.0.0.0',port=8080)
