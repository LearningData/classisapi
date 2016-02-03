import os

from flask import Flask, redirect, request, jsonify
from flask import make_response, abort, render_template, Response
from sqlalchemy import or_, and_

from app import app
from auth import requires_auth, restrict_administrator, client_id
from models import *
from services import create_school, create_api_user

@app.before_request
@requires_auth
def before_request(authenticated_user):
    global client_id
    global db
    if authenticated_user:
        client_id = authenticated_user.school.client_id
        school = authenticated_user.school

        if authenticated_user.user != 'administrator':
            db_url = 'mysql://' + os.environ.get('API_REMOTE_DB_AUTH', '') + \
                '@' + school.host + ':' + school.port + '/' + school.db
            db = connect_remote_db(db_url)

@app.route('/')
def index():
    return "This is Classis' API"

@app.route('/register', methods=['POST'])
@restrict_administrator
def register_api_user():
    if not request.json or not 'school_name' in request.json \
            or not 'client_id' in request.json \
            or not 'host' in request.json \
            or not 'db' in request.json:
        abort(400)

    epf_path = ''
    if 'epf_path' in request.json:
        epf_path = request.json['epf_path']
    port = ''
    if 'port' in request.json:
        port = request.json['port']
    city = ''
    if 'city' in request.json:
        city = request.json['city']
    email = ''
    if 'email' in request.json:
        email = request.json['email']

    school = create_school(
        request.json['school_name'],
        request.json['client_id'],
        request.json['host'],
        request.json['db'],
        epf_path,
        port,
        city
    )
    user = create_api_user(school.id, email)

    return jsonify({
        'user': user.user,
        'token': user.token,
        'client_id': school.client_id,
    }), 201

@app.route('/students', methods=['GET'])
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

@app.route('/students/<int:student_id>', methods=['GET'])
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

@app.route('/students/pictures', methods=['GET'])
def get_students_pictures():
    students = db.query(Student). \
            join(Student.info). \
            filter(Info.enrolstatus == 'C'). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'pictures': [student.get_pictures_json() for student in students]
        })

@app.route('/students/<int:student_id>/pictures', methods=['GET'])
def get_student_pictures(student_id):
    student = db.query(Student). \
            first()

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'pictures': student.get_pictures_json(),
        })

@app.route('/teachers', methods=['GET'])
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

@app.route('/teachers/<int:teacher_id>', methods=['GET'])
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

@app.route('/teachers/pictures', methods=['GET'])
def get_teachers_pictures():
    teachers = db.query(Teacher). \
            filter(and_(Teacher.nologin == 0, Teacher.username != 'administrator')). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'pictures': [teacher.get_pictures_json() for teacher in teachers]
        })

@app.route('/teachers/<int:teacher_id>/pictures', methods=['GET'])
def get_teacher_pictures(teacher_id):
    teacher = db.query(Teacher). \
            first()

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'pictures': teacher.get_pictures_json(),
        })

@app.route('/guardians', methods=['GET'])
def get_guardians():
    guardians = db.query(Guardian). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(guardians),
        'guardians': [guardian.json() for guardian in guardians]
        })

@app.route('/guardians/<int:guardian_id>', methods=['GET'])
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

@app.route('/classes', methods=['GET'])
def get_classes():
    classes = db.query(Class). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(classes),
        'classes': [teaching_class.json() for teaching_class in classes]
        })

@app.route('/classes/<int:class_id>', methods=['GET'])
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

@app.route('/classes/year/<int:year>', methods=['GET'])
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

@app.route('/classes/course/<course>', methods=['GET'])
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

@app.route('/cohorts', methods=['GET'])
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

@app.route('/cohorts/<int:cohort_id>', methods=['GET'])
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

@app.route('/cohorts/year/<int:year>', methods=['GET'])
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

@app.route('/cohorts/course/<course>', methods=['GET'])
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

@app.route('/communities', methods=['GET'])
def get_communities():
    communities = db.query(Community). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(communities),
        'communities': [community.json(community_dates = True) for community in communities]
        })

@app.route('/communities/type/<type>', methods=['GET'])
def get_communities_by_type(type):
    communities = db.query(Community). \
            filter(Community.type == type). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(communities),
        'communities': [community.json(community_dates = True) for community in communities]
        })

@app.route('/communities/<int:community_id>', methods=['GET'])
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

@app.route('/yeargroups', methods=['GET'])
def get_yeargroups():
    yeargroups = db.query(YearGroup). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(yeargroups),
        'yeargroups': [yeargroup.json() for yeargroup in yeargroups]
        })

@app.route('/homeworks', methods=['POST'])
def create_homework():
    if not request.json or not 'title' in request.json \
            or not 'class_id' in request.json \
            or not 'description' in request.json \
            or not 'author_id' in request.json \
            or not 'date_due' in request.json \
            or not 'date_set' in request.json :
        abort(400)

    class_group = db.query(Class).get(request.json['class_id'])
    author = db.query(Teacher).get(request.json['author_id'])

    homework =  Homework()
    homework.title = request.json['title']
    homework.description = request.json['description']
    homework.course_id = class_group.cohort.course_id
    homework.subject_id = class_group.subject_id
    homework.component_id = ''
    homework.stage = class_group.cohort.stage
    homework.def_name = 'raw score'
    homework.author = author.username
    homework.refs = ''
    db.add(homework)
    db.commit()

    date_due = request.json['date_due']
    date_set = request.json['date_set']
    if date_due == '' or date_set == '':
        date_due = date_set = datetime.date.today()

    mark = Mark()
    mark.date_due = date_due
    mark.date_set = date_set
    mark.topic = homework.title
    mark.homework_id = homework.id
    mark.def_name = 'raw score'
    mark.type = 'hw'
    mark.author = author.username
    db.add(mark)
    db.commit()

    midcid = MidCid()
    midcid.class_id = class_group.id
    midcid.mark_id = mark.id
    db.add(midcid)
    db.commit()

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'homeworks': homework.json()
        }), 201

@app.route('/homeworks', methods=['GET'])
def get_homeworks():
    homeworks = db.query(Homework). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(homeworks),
        'homeworks': [homework.json() for homework in homeworks]
        })

@app.route('/homeworks/<int:homework_id>', methods=['GET'])
def get_homework(homework_id):
    homework = db.query(Homework). \
            filter(Homework.id == homework_id). \
            first()

    if not homework:
        abort(404)

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'homeworks': homework.json()
        })

@app.route('/homeworks/stage/<stage>', methods=['GET'])
def get_homeworks_by_stage(stage):
    homeworks = db.query(Homework). \
            filter(Homework.stage == stage). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(homeworks),
        'homeworks': [homework.json() for homework in homeworks]
        })

@app.route('/homeworks/subject/<subject_id>', methods=['GET'])
def get_homeworks_by_subject(subject_id):
    homeworks = db.query(Homework). \
            filter(Homework.subject_id == subject_id). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(homeworks),
        'homeworks': [homework.json() for homework in homeworks]
        })

@app.route('/homeworks/class/<int:class_id>', methods=['GET'])
def get_homeworks_by_class(class_id):
    homeworks = db.query(Homework). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(homeworks),
        'homeworks': [homework.json() for homework in homeworks]
        })

