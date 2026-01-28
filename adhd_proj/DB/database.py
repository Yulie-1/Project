from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=True)
        # The sessionmaker creates an instance. It doesnt actually open a connection
        self.SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self):
        # Here i open a connection.  See context manager in db_func.py
        return self.SessionLocal()
    
    