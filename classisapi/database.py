import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(os.environ.get('API_DB_URL'), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import admin
    Base.metadata.create_all(bind=engine)

    from admin import User, School
    from services import create_school, create_api_user

    administrator = db_session.query(User).filter(User.user=='administrator').first()
    if not administrator:
        school = create_school('Admin School', '', '', '')
        administrator = create_api_user(
            school.id,
            'classisapi@learningdata.ie',
            'administrator'
        )
