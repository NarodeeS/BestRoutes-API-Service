import os
from dotenv import load_dotenv
from best_routes import app
from best_routes.directions_manager_thread import DirectionsManagerThread

load_dotenv()


directions_manager = DirectionsManagerThread(float(os.environ.get("CHECK_TIME")))
directions_manager.start()

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"))

