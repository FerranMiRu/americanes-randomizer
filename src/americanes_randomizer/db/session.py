from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


ENGINE = create_engine("sqlite:///database/americanes_randomizer.db")
DATABASE_SESSION = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
