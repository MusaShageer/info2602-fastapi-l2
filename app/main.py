from fastapi import FastAPI
from app.database import create_db_and_tables
app = FastAPI()


@app.get('/')
def hello_world():
    return 'Hello, World!'