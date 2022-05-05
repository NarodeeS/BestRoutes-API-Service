import os
from best_routes import app

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"), load_dotenv=True)
