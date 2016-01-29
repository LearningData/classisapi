import os
from models import Student, Info, Teacher, Guardian, Class, connect_db
from flask import Flask, redirect, request, jsonify, make_response, abort
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

app = Flask(__name__)

db = connect_db(os.environ.get('DB_URL'))

client_id = 'demo'

@app.route('/')
def index():
    return redirect("api/v2.0")

@app.route('/api/v2.0')
def api():
    return "This is Classis' API"

@app.route('/api/v2.0/students', methods=['GET'])
def get_students():
    students = db.query(Student). \
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
    student = db.query(Student). \
            filter(Student.id == student_id). \
            first()

    if not student:
        abort(404)

    return jsonify({
        'client_id': client_id,
        'count': 1,
        'students': student.json()
        })

@app.route('/api/v2.0/teachers', methods=['GET'])
def get_teachers():
    teachers = db.query(Teacher). \
            filter(or_(Teacher.role == 'teacher', Teacher.role == 'admin')). \
            filter(Teacher.username != 'administrator'). \
            all()

    return jsonify({
        'client_id': client_id,
        'count': len(teachers),
        'teachers': [teacher.json() for teacher in teachers]
        })

@app.route('/api/v2.0/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = db.query(Teacher). \
            filter(Teacher.id == teacher_id). \
            filter(Teacher.username != 'administrator'). \
            first()

    if not teacher:
        abort(404)

    return jsonify({
        'client_id': client_id,
        'count': 1,
        'teachers': teacher.json()
        })

@app.route('/api/v2.0/guardians', methods=['GET'])
def get_guardians():
    guardians = db.query(Guardian). \
            all()

    return jsonify({
        'client_id': client_id,
        'count': len(guardians),
        'guardians': [guardian.json() for guardian in guardians]
        })

@app.route('/api/v2.0/guardians/<int:guardian_id>', methods=['GET'])
def get_guardian(guardian_id):
    guardian = db.query(Guardian). \
            filter(Guardian.id == guardian_id). \
            first()

    if not guardian:
        abort(404)

    return jsonify({
        'client_id': client_id,
        'count': 1,
        'guardians': guardian.json()
        })

@app.route('/api/v2.0/classes', methods=['GET'])
def get_classes():
    classes = db.query(Class). \
            all()

    return jsonify({
        'client_id': client_id,
        'count': len(classes),
        'classes': [teaching_class.json() for teaching_class in classes]
        })

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=os.environ.get('PORT', 5000),
            debug=os.environ.get('DEBUG', True))
