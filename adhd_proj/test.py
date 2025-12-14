from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")  
PASSWORD = os.getenv("DB_PASSWORD")  
HOST = os.getenv("DB_HOST")  
PORT = os.getenv("DB_PORT") 
DATABASE_NAME = os.getenv("DB_DATABASE_NAME") 

print("Database configuration loaded:")
print(f"USERNAME: {USERNAME}")
print(f"PASSWORD: {PASSWORD}")
print(f"HOST: {HOST}")
print(f"PORT: {PORT}")
print(f"DATABASE_NAME: {DATABASE_NAME}")