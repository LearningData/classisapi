import os
import base64

from classisapi import config

def get_title(title):
    title_key = str(title)
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
    return str(titles[title_key]) if title_key in titles else ''

def get_user_picture(epfusername, client_id=''):
    images_path = config['AVATARS_DIR'] + '/' + client_id

    encoded_image = None
    file_name = None

    image = {}

    if epfusername != '':
        file_name = epfusername + '.jpeg'
        file = images_path + '/' + file_name
        if os.path.exists(file):
            with open(file, 'rb') as image:
                encoded_image = base64.b64encode(image.read())
        else:
            file_name = None

    image = {
        'base64': encoded_image,
        'name': file_name
    }

    return image

def get_student_reports(epfusername, client_id=''):
    reports_path = config['REPORTS_DIR'] + '/' + client_id

    reports = []

    if epfusername != '':
        dir = reports_path + '/' + epfusername
        if os.path.exists(dir):
            for file in os.listdir(dir):
                with open(dir + '/' + file, 'rb') as pdf:
                    encoded_pdf = base64.b64encode(pdf.read())

                    report = {
                        'base64': encoded_pdf,
                        'name': file
                    }

                    reports.append(report)

    return reports
