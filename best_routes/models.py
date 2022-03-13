from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    telegram_id = Column(String(50), default=None)
    mail_tracking = Column(Integer(), default=0)
    telegram_tracking = Column(Integer(), default=0)
    relationship("Token")


class Token(Base):
    __tablename__ = "tokens"

    value = Column(String(), nullable=False, primary_key=True)
    user_id = Column(Integer(), ForeignKey(User.id), nullable=False, primary_key=True)
