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

    gidsids = relationship("GidSid",
                        foreign_keys='GidSid.student_id',
                        lazy='subquery',
                        )

    classes = relationship("CidSid",
                        foreign_keys='CidSid.student_id',
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
            'classes': [class_member.class_id for class_member in self.classes],
        }


class Info(Base):
    __tablename__ = 'info'

    id = Column('student_id', Integer, ForeignKey('student.id'), primary_key=True)


class Teacher(Base):
    __tablename__ = 'users'

    id = Column('uid', Integer, primary_key=True)

    classes = relationship("TidCid",
                        foreign_keys='TidCid.teacher_id',
                        lazy='subquery',
                        )

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
            'classes': [teaching_class.class_id for teaching_class in self.classes],
        }


class GidSid(Base):
    __tablename__ = 'gidsid'

    student_id = Column("student_id", Integer, ForeignKey("student.id"), primary_key=True)
    guardian_id = Column("guardian_id", Integer, ForeignKey("guardian.id"), primary_key=True)

    def json(self):
        return {
            'id': self.student_id,
            'priority': self.priority,
            'mailing': self.mailing,
            'relationship': self.relationship,
        }


class CidSid(Base):
    __tablename__ = 'cidsid'

    student_id = Column("student_id", Integer, ForeignKey("student.id"), primary_key=True)
    class_id = Column("class_id", Integer, ForeignKey("class.id"), primary_key=True)


class TidCid(Base):
    __tablename__ = 'tidcid'

    teacher_id = Column("teacher_id", Integer, ForeignKey("users.username"), primary_key=True)
    class_id = Column("class_id", Integer, ForeignKey("class.id"), primary_key=True)


class Course(Base):
    __tablename__ = 'course'

    id = Column('id', Integer, primary_key=True)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class CohidComid(Base):
    __tablename__ = 'cohidcomid'

    cohort_id = Column("cohort_id", Integer, ForeignKey("cohort.id"), primary_key=True)
    community_id = Column("community_id", Integer, ForeignKey("community.id"), primary_key=True)

class ComidSid(Base):
    __tablename__ = 'comidsid'

    student_id = Column("student_id", Integer, ForeignKey("student.id"), primary_key=True)
    community_id = Column("community_id", Integer, ForeignKey("community.id"), primary_key=True)

    def is_active(self):
        if self.leavingdate == None:
            return True
        return False

    def json(self):
        return {
            'id': self.student_id,
            'joining_date': str(self.joiningdate),
            'leaving_date': str(self.leavingdate),
            'active': self.is_active()
        }

class Community(Base):
    __tablename__ = 'community'

    id = Column('id', Integer, primary_key=True)

    cohidcomids = relationship("CohidComid",
                        foreign_keys='CohidComid.community_id',
                        lazy='subquery',
                        )

    students = relationship("ComidSid",
                        foreign_keys='ComidSid.community_id',
                        lazy='subquery',
                        )
    def json(self, community_dates = False):
        students = [student.json() for student in self.students]
        if not community_dates:
            students = [student.student_id for student in self.students if student.is_active()]

        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'year': str(self.year),
            'capacity': self.capacity,
            'detail': self.detail,
            'students': students,
        }


class Cohort(Base):
    __tablename__ = 'cohort'

    id = Column("id", Integer, primary_key=True)
    course_id = Column('course_id', Integer, ForeignKey('course.id'), primary_key=True)

    classes = relationship("Class",
                        foreign_keys="Class.cohort_id",
                        primaryjoin="Cohort.id==Class.cohort_id",
                        lazy='subquery',
                        )

    communities = relationship("Community",
                        secondary="cohidcomid",
                        primaryjoin=id==CohidComid.cohort_id,
                        secondaryjoin=Community.id==CohidComid.community_id,
                        lazy='subquery',
                        )

    def json(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_name': self.course.name,
            'stage': self.stage,
            'year': self.year,
            'classes': [teaching_class.id for teaching_class in self.classes],
            'communities': [community.json() for community in self.communities],
        }


class Guardian(Base):
    __tablename__ = 'guardian'

    id = Column('id', Integer, primary_key=True)

    gidsids = relationship("GidSid",
                        foreign_keys='GidSid.guardian_id',
                        lazy='subquery',
                        )

    students = relationship("Student",
                        secondary="gidsid",
                        primaryjoin=id==GidSid.guardian_id,
                        secondaryjoin=Student.id==GidSid.student_id,
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
            'students': [gidsid.json() for gidsid in self.gidsids],
        }


class Subject(Base):
    __tablename__ = 'subject'

    id = Column('id', Integer, primary_key=True)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Class(Base):
    __tablename__ = 'class'

    id = Column('id', Integer, primary_key=True)
    cohort_id = Column('cohort_id', Integer, ForeignKey('cohort.id'), primary_key=True)
    subject_id = Column('subject_id', Integer, ForeignKey('subject.id'), primary_key=True)

    students = relationship("CidSid",
                        foreign_keys='CidSid.class_id',
                        lazy='subquery',
                        )

    teachers = relationship("TidCid",
                        foreign_keys='TidCid.class_id',
                        lazy='subquery',
                        )

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name,
            'stage': self.cohort.stage,
            'year': self.cohort.year,
            'course_id': self.cohort.course_id,
            'course_name': self.cohort.course.name,
            'students': [student.student_id for student in self.students],
            'teachers': [teacher.teacher_id for teacher in self.teachers],
        }


class Section(Base):
    __tablename__ = 'section'

    id = Column('id', Integer, primary_key=True)


class YearGroup(Base):
    __tablename__ = 'yeargroup'

    id = Column('id', String, primary_key=True)
    section_id = Column('section_id', Integer,  ForeignKey('section.id'), primary_key=True)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'sequence': self.sequence,
            'section_id': self.section_id,
            'section_name': self.section.name,
            'section_sequence': self.section.sequence,
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

def get_curriculum_year(db):
    curriculum_year = db.query(Community). \
            filter(Community.name == "curriculum year"). \
            group_by(Community.year). \
            first()

    return curriculum_year.year
