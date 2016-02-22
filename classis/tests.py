import os
import shutil
import unittest
import base64
from PIL import Image

from services import get_title, get_user_picture, get_student_reports


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.name = 'epf1'

        self.image = create_mock_file(self.name + '.jpeg')

        self.empty_get_user_picture = get_file_dict()
        self.completed_get_user_picture = get_file_dict(self.image)

        self.reports_dir = '/tmp/' + self.name
        self.report = create_mock_file(self.name + '.pdf', self.reports_dir)

        self.reports = []
        self.empty_get_student_reports = []
        self.reports.append(get_file_dict(self.report))
        self.completed_get_student_reports = self.reports

    def tearDown(self):
        os.remove(self.image)
        shutil.rmtree(self.reports_dir)

    def test_get_title_empty_returns_empty_string(self):
        assert get_title('') == ''

    def test_get_title_1_returns_mr(self):
        assert get_title(1) == 'mr'

    def test_get_title_1000_returns_empty_string(self):
        assert get_title(1000) == ''

    def test_get_title_string_returns_empty_string(self):
        assert get_title('test') == ''

    def test_get_user_picture_without_epfusername_returns_empty_json(self):
        assert get_user_picture('') == self.empty_get_user_picture

    def test_get_user_picture_no_file_returns_empty_json(self):
        assert get_user_picture('epf2') == self.empty_get_user_picture

    def test_get_user_picture_with_epfusername_returns_complete_json(self):
        assert get_user_picture('epf1') == self.completed_get_user_picture

    def test_get_student_reports_without_epfusername_returns_empty_json(self):
        assert get_student_reports('') == self.empty_get_student_reports

    def test_get_student_reports_no_files_returns_empty_json(self):
        assert get_student_reports('epf2') == self.empty_get_student_reports

    def test_get_student_reports_with_epfusername_returns_complete_json(self):
        assert get_student_reports('epf1') == self.completed_get_student_reports

    def test_get_student_reports_with_multiple_reports_returns_multiple_reports(self):
        new_report = create_mock_file(self.name + '2.pdf', self.reports_dir)
        new_report_dict = get_file_dict(new_report)
        self.reports.append(new_report_dict)
        assert len(get_student_reports('epf1')) == len(self.reports)


def create_mock_file(file_name, path='/tmp'):
    if not os.path.exists(path):
        os.makedirs(path)

    file = '%s/%s' % (path, file_name)
    image = Image.new("RGB", (255,255), "#000")
    image.save(file)

    return file

def get_file_dict(file_path=''):
    encoded_file = None
    file_name = None

    if file_path != '':
        with open(file_path, 'rb') as file:
            encoded_file = base64.b64encode(file.read())

            return {
                'base64': encoded_file,
                'name': os.path.basename(file_path)
            }

    return {
        'base64': None,
        'name': None
    }

if __name__ == '__main__':
    unittest.main()
