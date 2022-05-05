import os
from flask import Flask
from dotenv import load_dotenv
from best_routes.directions_manager_thread import DirectionsManagerThread

load_dotenv()

directions_manager = DirectionsManagerThread(float(os.environ.get("CHECK_TIME")))
directions_manager.start()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


from best_routes import routes
