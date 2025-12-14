from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=True)
        # The sessionmaker creates an instance. It doesnt actually open a connection
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(self.engine) # doesnt touch existing tables.

    def get_session(self):
        # Here i open a connection.  See context manager in db_func.py
        return self.SessionLocal()
    
    