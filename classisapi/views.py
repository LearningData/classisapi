import os

from flask import Flask, redirect, request, jsonify, g, url_for
from flask import make_response, abort, render_template, Response
from sqlalchemy import or_, and_

from classisapi import app, config
from classis.models import *
from auth import requires_auth, restrict_administrator, client_id
from services import create_school, create_api_user

@app.before_request
@requires_auth
def before_request(authenticated_user):
    global client_id
    global db
    if authenticated_user:
        school = authenticated_user.school

        db = None
        if authenticated_user.user != config['ADMINISTRATOR_NAME']:
            client_id = school.client_id
            db_url = 'mysql://' + config['REMOTE_DB_AUTH'] + \
                '@' + school.host + ':' + school.port + '/' + school.db
            db = connect_remote_db(db_url)
        g.db = db

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.errorhandler(400)
def invalid_request(error):
        return make_response(jsonify({'error': 'Invalid request'}), 400)

@app.errorhandler(401)
def invalid_credentials(error):
        return make_response(jsonify({'error': 'Invalid credentials'}), 401)

@app.errorhandler(403)
def forbidden(error):
        return make_response(jsonify({'error': 'Forbidden'}), 403)

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(415)
def invalid_content_type(error):
        return make_response(jsonify({'error': 'Invalid Content-Type'}), 415)

@app.route('/')
def index():
    """Graph API."""

    return render_template('index.html')

@app.route('/help', methods = ['GET'])
def help():
    """List with all available API endpoints."""

    import urllib

    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = urllib.unquote(','.join(rule.methods))
            url = urllib.unquote(rule.rule). \
                    replace('>', ']'). \
                    replace('<', '[')

            func_list[rule.endpoint] = {
                'url': url,
                'info': app.view_functions[rule.endpoint].__doc__,
                'methods': methods,
            }

    return jsonify(func_list)

@app.route('/register', methods=['POST'])
@restrict_administrator
def register_api_user():
    """Register a user. Restricted to administrator. """ \
    """Requires school_name, client_id, host and db in JSON format."""

    if not request.json:
        abort(415)
    else:
        if not 'school_name' in request.json \
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
    """List with all current or previous students."""

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
    """List information for a specific student."""

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
    """Get pictures for all current students."""

    students = db.query(Student). \
            join(Student.info). \
            filter(Info.enrolstatus == 'C'). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(students),
        'pictures': [student.get_pictures_json(client_id) for student in students]
        })

@app.route('/students/<int:student_id>/pictures', methods=['GET'])
def get_student_pictures(student_id):
    """Get picture for a specific student."""

    student = db.query(Student). \
            filter(Student.id == student_id). \
            first()

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'pictures': student.get_pictures_json(client_id),
        })

@app.route('/teachers', methods=['GET'])
def get_teachers():
    """Get all teachers with roles teacher and admin."""

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
    """Get a teacher info."""

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
    """Get pictures for all current teachers."""

    teachers = db.query(Teacher). \
            filter(and_(Teacher.nologin == 0, Teacher.username != 'administrator')). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(teachers),
        'pictures': [teacher.get_pictures_json(client_id) for teacher in teachers]
        })

@app.route('/teachers/<int:teacher_id>/pictures', methods=['GET'])
def get_teacher_pictures(teacher_id):
    """Get a teacher's profile picture."""

    teacher = db.query(Teacher). \
            filter(Teacher.id == teacher_id). \
            first()

    return jsonify({
        '_client_id': client_id,
        '_count': 1,
        'pictures': teacher.get_pictures_json(client_id),
        })

@app.route('/guardians', methods=['GET'])
def get_guardians():
    """Get all guardians."""

    guardians = db.query(Guardian). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(guardians),
        'guardians': [guardian.json() for guardian in guardians]
        })

@app.route('/guardians/active', methods=['GET'])
def get_active_guardians():
    """Get all guardians for current students."""

    guardians = db.query(Guardian). \
            outerjoin(Guardian.students). \
            outerjoin(Student.info). \
            filter(Info.enrolstatus == 'C'). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(guardians),
        'guardians': [guardian.json() for guardian in guardians]
        })

@app.route('/guardians/<int:guardian_id>', methods=['GET'])
def get_guardian(guardian_id):
    """Get a guardian's information."""

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
    """Get all available classes."""

    classes = db.query(Class). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(classes),
        'classes': [teaching_class.json() for teaching_class in classes]
        })

@app.route('/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    """Get a class by class_id."""

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
    """Get a class info by the academic year."""

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
    """Get a class info by the course_id."""

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
    """Get a complete list of cohorts."""

    cohorts = db.query(Cohort). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(cohorts),
        'cohorts': [cohort.json() for cohort in cohorts]
        })

@app.route('/cohorts/<int:cohort_id>', methods=['GET'])
def get_cohort(cohort_id):
    """Get a cohort by the cohort_id."""

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
    """Get cohorts by the academic year."""

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
    """Get cohorts by the course_id."""

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
    """Get all available communities."""

    communities = db.query(Community). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(communities),
        'communities': [community.json(community_dates = True) for community in communities]
        })

@app.route('/communities/type/<type>', methods=['GET'])
def get_communities_by_type(type):
    """Get communities by their type: year, form, etc."""

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
    """Get a community by its id."""

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
    """Get a list with the yeargroups."""

    yeargroups = db.query(YearGroup). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(yeargroups),
        'yeargroups': [yeargroup.json() for yeargroup in yeargroups]
        })

@app.route('/homeworks', methods=['POST'])
def create_homework():
    """Post a homework for a class. """ \
    """Requires title, class_id, description, author_id, """ \
    """date_due and date_set in JSON format"""

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
    """Get all the available homeworks."""

    homeworks = db.query(Homework). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(homeworks),
        'homeworks': [homework.json() for homework in homeworks]
        })

@app.route('/homeworks/<int:homework_id>', methods=['GET'])
def get_homework(homework_id):
    """Get a homework by its id."""

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
    """Get all homeworks for a particular stage."""

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
    """Get all homeworks for a subject."""

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
    """Get all homeworks for a class."""

    homeworks = db.query(Homework). \
            all()

    return jsonify({
        '_client_id': client_id,
        '_count': len(homeworks),
        'homeworks': [homework.json() for homework in homeworks]
        })

