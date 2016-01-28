from sqlalchemy import create_engine, or_
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, relationship

Base = automap_base()


class Student(Base):
    __tablename__ = 'student'

    id = Column('id', Integer, ForeignKey('info.student_id'), primary_key=True)

    info_id = relationship("Info",
                        foreign_keys='Info.id',
                        lazy='subquery',
                        )

    def active(self):
        if self.info.enrolstatus == 'C':
            return True
        return False

    def json(self):
        return {
            'id': self.id,
            'name': self.forename,
            'last_name': self.surname,
            'gender': self.gender,
            'date_of_birth': str(self.dob),
            'active': self.active(),
            'enroll_number': self.info.formerupn,
            'username': self.info.epfusername,
            'email': self.info.email,
            'staff_child': self.info.staffchild,
            'nationality': self.info.nationality,
            'entry_date': str(self.info.entrydate),
            'leaving_date': str(self.info.leavingdate),
        }


class Info(Base):
    __tablename__ = 'info'

    id = Column('student_id', Integer, ForeignKey('student.id'), primary_key=True)

def connect_db(db_url):
    engine = create_engine(db_url, convert_unicode=True)
    Base.prepare(engine, reflect=True)

    return Session(engine)
