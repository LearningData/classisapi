import os
from flask import Flask, redirect, request, jsonify, make_response, abort

from sqlalchemy import create_engine, or_
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, relationship

app = Flask(__name__)

Base = automap_base()
engine = create_engine(os.environ.get('DB_URL'), convert_unicode=True)

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

Base.prepare(engine, reflect=True)
session = Session(engine)

client_id = 'demo'

@app.route('/')
def index():
    return redirect("api/v2.0")

@app.route('/api/v2.0')
def api():
    return "This is Classis' API"

@app.route('/api/v2.0/students', methods=['GET'])
def get_students():
    students = session.query(Student). \
            join(Student.info). \
            filter(or_(Info.enrolstatus == 'C', Info.enrolstatus == 'P')). \
            all()

    return jsonify({
        'client_id': client_id,
        'count': len(students),
        'students': [student.json() for student in students]
        })

@app.route('/api/v2.0/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = session.query(Student). \
            filter(Student.id == student_id). \
            first()

    if not student:
        abort(404)

    return jsonify({
        'client_id': client_id,
        'count': 1,
        'students': student.json()
        })

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=os.environ.get('PORT', 5000),
            debug=os.environ.get('DEBUG', True))
