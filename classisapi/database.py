import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from classisapi import config

engine = create_engine(config['DB_URL'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from admin import User, School
    from services import create_school, create_api_user

    try:
        administrator = User.query. \
                filter(User.user==config['ADMINISTRATOR_NAME']).first()
        if not administrator:
            school = create_school('Admin School', '', '', '')
            administrator = create_api_user(
                school.id,
                config['ADMINISTRATOR_EMAIL'],
                config['ADMINISTRATOR_NAME']
            )
    except:
        pass
