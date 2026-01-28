from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")  
PASSWORD = os.getenv("DB_PASSWORD")  
HOST = os.getenv("DB_HOST")  
PORT = os.getenv("DB_PORT") 
DATABASE_NAME = os.getenv("DB_DATABASE_NAME") 

db_url = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"
print(f"Connecting to: {db_url.replace(PASSWORD, '***')}")

try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    if "tasks" in tables and "categories" in tables:
        print("SUCCESS: Tables exist.")
    else:
        print("FAILURE: Tables missing.")
except Exception as e:
    print(f"Connection failed: {e}")
