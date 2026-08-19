from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
