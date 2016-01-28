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

    def is_active(self):
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
            'active': self.is_active(),
            'enroll_number': self.info.formerupn,
            'username': 'demo' + self.info.epfusername,
            'epf_username': self.info.epfusername,
            'email': self.info.email,
            'staff_child': self.info.staffchild,
            'nationality': self.info.nationality,
            'language': self.info.language,
            'entry_date': str(self.info.entrydate),
            'leaving_date': str(self.info.leavingdate),
        }


class Info(Base):
    __tablename__ = 'info'

    id = Column('student_id', Integer, ForeignKey('student.id'), primary_key=True)


class Teacher(Base):
    __tablename__ = 'users'

    id = Column('uid', Integer, primary_key=True)

    def is_active(self):
        if self.nologin:
            return False
        return True

    def get_title(self):
	titles = {'': '',
            '0': '',
            '1': 'mr',
            '2': 'mrs',
            '3': 'srd',
            '4': 'srada',
            '5': 'miss',
            '6': 'dr',
            '7': 'ms',
            '8': 'major'
            };
        return str(titles[str(self.title)])

    def json(self):
        return {
            'id': self.id,
            'name': self.forename,
            'last_name': self.surname,
            'date_of_birth': str(self.dob),
            'active': self.is_active(),
            'username': self.username,
            'epf_username': self.epfusername,
            'email': self.email,
            'title': self.get_title(),
            'language': self.language,
            'role': self.role,
            'personal_email': self.personalemail,
            'mobile_phone': str(self.mobilephone),
        }


def connect_db(db_url):
    engine = create_engine(db_url, convert_unicode=True)
    Base.prepare(engine, reflect=True)

    return Session(engine)
