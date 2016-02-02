import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import Session, relationship

from database import Base, engine

class School(Base):
    __tablename__ = 'school'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    client_id = Column(String(100))
    host = Column(String(16))
    port = Column(String(6), default='3306')
    db = Column(String(15), unique=True)
    city = Column(String(150))

    def __init__(self, host=None, db=None):
        self.host = host
        self.db = db

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user = Column(String(16), unique=True)
    token = Column(String(20), unique=True)
    school_id = Column(Integer, ForeignKey('school.id'))
    email = Column(String(120))
    status = Column(Boolean, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_request = Column(DateTime)
    requests_count = Column(Integer, default=0)

    school = relationship("School",
                        foreign_keys=school_id,
                        lazy='subquery',
                        )

    def __init__(self, user=None, token=None):
        self.user = user
        self.token = email
