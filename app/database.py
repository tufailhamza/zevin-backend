from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration - matching RFL.py exactly
db_config = {
    'user': 'doadmin',
    'password': 'AVNS_xKVgSkiz4gkauzSux86',
    'host': 'db-mysql-nyc3-25707-do-user-19616823-0.l.db.ondigitalocean.com',
    'port': 25060,
    'database': 'defaultdb'
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

