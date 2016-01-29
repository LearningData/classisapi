from sqlalchemy import create_engine, or_
from sqlalchemy import Column, Integer, String, ForeignKey, Table
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
            'title': get_title(self.title),
            'language': self.language,
            'role': self.role,
            'personal_email': self.personalemail,
            'mobile_phone': str(self.mobilephone),
        }

class Gidsid(Base):
    __tablename__ = 'gidsid'

    student_id = Column("student_id", Integer, ForeignKey("student.id"), primary_key=True)
    guardian_id = Column("guardian_id", Integer, ForeignKey("guardian.id"), primary_key=True)

class Guardian(Base):
    __tablename__ = 'guardian'

    id = Column('id', Integer, primary_key=True)

    students = relationship("Student",
                        secondary="gidsid",
                        primaryjoin=id==Gidsid.guardian_id,
                        secondaryjoin=Student.id==Gidsid.student_id,
                        lazy='subquery',
                        )

    def is_active(self):
        for student in self.students:
            if student.is_active():
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
            'username': self.epfusername,
            'epf_username': self.epfusername,
            'email': self.email,
            'title': get_title(self.title),
            'language': self.language,
            'nationality': self.nationality,
            'profession': self.profession,
            'private': self.private,
            'students': [student.id for student in self.students],
        }


def connect_db(db_url):
    engine = create_engine(db_url, convert_unicode=True)
    Base.prepare(engine, reflect=True)

    return Session(engine)

def get_title(title):
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
    return str(titles[str(title)])
