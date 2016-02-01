import os
from models import Student, Info, Teacher, Guardian, Cohort, Class, Community, connect_db, get_curriculum_year
from flask import Flask, redirect, request, jsonify, make_response, abort
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

app = Flask(__name__)

db = connect_db(os.environ.get('DB_URL') + "?charset=utf8")

client_id = 'demo'
year = get_curriculum_year(db)


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
        '_client_id': client_id,
        '_count': len(students),
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
        '_client_id': client_id,
        '_count': 1,
        'students': student.json()
        })

@app.route('/api/v2.0/teachers', methods=['GET'])
def get_teachers():
    teachers = db.query(Teacher). \
            filter(or_(Teacher.role == 'teacher', Teacher.role == 'admin')). \
            filter(Teacher.username != 'administrator'). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(teachers),
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
        '_client_id': client_id,
        '_count': 1,
        'teachers': teacher.json()
        })

@app.route('/api/v2.0/guardians', methods=['GET'])
def get_guardians():
    guardians = db.query(Guardian). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(guardians),
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
        '_client_id': client_id,
        '_count': 1,
        'guardians': guardian.json()
        })

@app.route('/api/v2.0/classes', methods=['GET'])
def get_classes():
    classes = db.query(Class). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(classes),
        'classes': [teaching_class.json() for teaching_class in classes]
        })

@app.route('/api/v2.0/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    teaching_class = db.query(Class). \
            filter(Class.id == class_id). \
            first()

    if not teaching_class:
        abort(404)

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'classes': teaching_class.json()
        })

@app.route('/api/v2.0/classes/year/<int:year>', methods=['GET'])
def get_class_by_year(year):
    classes = db.query(Class). \
            join(Class.cohort).\
            filter(Cohort.year == year). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(classes),
        'classes': [teaching_class.json() for teaching_class in classes]
        })

@app.route('/api/v2.0/classes/course/<course>', methods=['GET'])
def get_class_by_course(course):
    classes = db.query(Class). \
            join(Class.cohort).\
            filter(Cohort.course_id == course). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(classes),
        'classes': [teaching_class.json() for teaching_class in classes]
        })

@app.route('/api/v2.0/cohorts', methods=['GET'])
def get_cohorts():
    cohorts = db.query(Cohort). \
            filter(Cohort.year == year). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(cohorts),
        '_academic_year': year,
        'cohorts': [cohort.json() for cohort in cohorts]
        })

@app.route('/api/v2.0/cohorts/<int:cohort_id>', methods=['GET'])
def get_cohort(cohort_id):
    cohort = db.query(Cohort). \
            filter(Cohort.id == cohort_id). \
            first()

    if not cohort:
        abort(404)

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'cohorts': cohort.json()
        })

@app.route('/api/v2.0/cohorts/year/<int:year>', methods=['GET'])
def get_cohorts_by_year(year):
    cohorts = db.query(Cohort). \
            filter(Cohort.year == year). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(cohorts),
        '_academic_year': year,
        'cohorts': [cohort.json() for cohort in cohorts]
        })

@app.route('/api/v2.0/cohorts/course/<course>', methods=['GET'])
def get_cohorts_by_course(course):
    cohorts = db.query(Cohort). \
            filter(and_(Cohort.year == year, Cohort.course_id == course)). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(cohorts),
        '_academic_year': year,
        'cohorts': [cohort.json() for cohort in cohorts]
        })

@app.route('/api/v2.0/communities', methods=['GET'])
def get_communities():
    communities = db.query(Community). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(communities),
        'communities': [community.json(community_dates = True) for community in communities]
        })

@app.route('/api/v2.0/communities/type/<type>', methods=['GET'])
def get_communities_by_type(type):
    communities = db.query(Community). \
            filter(Community.type == type). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(communities),
        'communities': [community.json(community_dates = True) for community in communities]
        })

@app.route('/api/v2.0/communities/<int:community_id>', methods=['GET'])
def get_community(community_id):
    community = db.query(Community). \
            filter(Community.id == community_id). \
            first()

    if not community:
        abort(404)

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'communities': community.json(community_dates = True)
        })

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=os.environ.get('PORT', 5000),
            debug=os.environ.get('DEBUG', True))
