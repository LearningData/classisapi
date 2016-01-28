import os
from models import Student, Info, connect_db
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

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=os.environ.get('PORT', 5000),
            debug=os.environ.get('DEBUG', True))
