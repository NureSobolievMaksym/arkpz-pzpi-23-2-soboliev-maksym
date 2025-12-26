import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@localhost/smartclimate_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Спеціальна функція для очікування БД
def wait_for_db():
    max_retries = 10
    retry_interval = 2
    for _ in range(max_retries):
        try:
            with engine.connect() as connection:
                print("Database connected!")
                return
        except OperationalError:
            print("Database not ready yet, retrying...")
            time.sleep(retry_interval)
    raise Exception("Could not connect to database after several retries")

# Викликаємо перевірку при імпорті
if "localhost" not in DATABASE_URL: # Перевірка, щоб не чекати при локальних тестах без докера
    wait_for_db()