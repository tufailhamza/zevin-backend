from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - using environment variables for security
# Set these in your .env file (see .env.example)
db_config = {
    'user': os.getenv('DB_USER', 'doadmin'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'db-mysql-nyc3-25707-do-user-19616823-0.l.db.ondigitalocean.com'),
    'port': os.getenv('DB_PORT', '25060'),
    'database': os.getenv('DB_NAME', 'defaultdb')
}

# Create SQLAlchemy connection string
db_connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Create engine - matching RFL.py approach exactly
engine = create_engine(db_connection_string)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

