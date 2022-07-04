from flask import Flask
from flask_restful import Api
from app.ressources.converter import Convert_to_PDF
from app.ressources.health import Health
import yaml
from yaml.loader import SafeLoader
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)

    UPLOAD_FOLDER = os.path.join("app", "uploads")

    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    # allowed file types, none of these has an alpha-channel, which is important
    app.config['ALLOWED_EXTENSIONS'] = {"image/png", "image/jpeg", "application/pdf"}

    # Do not use this. I do it with request.content_length to enforce one valid Error Return Message
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000

    app.config['CORS_HEADERS'] = 'Content-Type'
    cors = CORS(app,resources={r"/api/*": {"origins": "*"}})


    # now reading Error Yaml and bring it as Variable to Flask APP Config
    pathname = os.path.join("app", "conf", "ErrorNumbers", "ErrorNumbers.yaml")

    with open(pathname) as f:
       data = yaml.load(f, Loader=SafeLoader)
    app.config['ERRORNR'] = data
    register_resources(app)
    print("Flask App document-converter-to pdf running")

    return app

def register_resources(app):
    api = Api(app)
    api.add_resource(Convert_to_PDF, '/document-converter-pdf/v1/convert')
    api.add_resource(Health, '/actuator/health')