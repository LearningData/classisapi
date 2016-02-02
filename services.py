from models import Community, Student, Teacher

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

def get_user_picture(epfusername):
    return epfusername + ".jpeg"
