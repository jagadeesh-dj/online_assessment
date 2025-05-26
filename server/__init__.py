from flask import Flask, Blueprint
from server.extensions import db

api = Blueprint('api', __name__, url_prefix="/api/v1/")

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:1234@localhost:3306/assessement"

    db.init_app(app)
    
    app.register_blueprint(api)
    
    return app