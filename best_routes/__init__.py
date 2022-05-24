import os
from flask import Flask
from dotenv import load_dotenv
from best_routes.directions_manager_thread import DirectionsManagerThread
from best_routes.routes import developer_blueprint, base_blueprint, user_blueprint

load_dotenv()

directions_manager = DirectionsManagerThread(float(os.environ.get("CHECK_TIME")))
directions_manager.start()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.register_blueprint(developer_blueprint)
app.register_blueprint(base_blueprint)
app.register_blueprint(user_blueprint)
