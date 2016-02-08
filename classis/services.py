import os
import base64

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

def get_user_picture(epfusername, images_path = '/tmp'):
    encoded_image = None
    file_name = epfusername + '.jpeg'

    image = {}

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

