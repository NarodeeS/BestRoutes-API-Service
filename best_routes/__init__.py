import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_POOL_SIZE"] = 30
app.config["SQLALCHEMY_MAX_OVERFLOW"] = -1
db = SQLAlchemy(app)
app.secret_key = os.getenv("SECRET_KEY")


from best_routes import routes
