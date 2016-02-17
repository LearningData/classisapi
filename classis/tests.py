import os
import unittest
import base64
from PIL import Image

from services import get_title, get_user_picture


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.name = 'epf1'
        self.file_name = self.name + '.jpeg'

        self.file = '/tmp/%s' % self.file_name
        image = Image.new("RGB", (255,255), "#000")
        image.save(self.file)

        encoded_image = None
        with open(self.file, 'rb') as image:
            encoded_image = base64.b64encode(image.read())

        self.empty_get_user_picture = {
            'base64': None,
            'name': None
        }

        self.completed_get_user_picture = {
            'base64': encoded_image,
            'name': self.file_name
        }

    def tearDown(self):
        os.remove(self.file)

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


if __name__ == '__main__':
    unittest.main()
