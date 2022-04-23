import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


load_dotenv()

engine = create_engine(os.environ.get("DATABASE_URL"))
Base = declarative_base()
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
db_session = Session()
