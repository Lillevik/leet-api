from flask import Flask
from app import config
from flask_cors import CORS

app = Flask(__name__)
from app import views
CORS(app)
app.config.from_object(config)