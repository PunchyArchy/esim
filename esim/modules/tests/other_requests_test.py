""" Тесты модуля с прочими запросами """

import unittest
import os
from esim.modules import other_requests
from esim.modules import auth


class OtherRequestTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(OtherRequestTest, self).__init__(*args, **kwargs)
        self.dbname = os.environ.get('DATABASE_NAME')
        self.dbuser = os.environ.get('DATABASE_USERNAME')
        self.dbpass = os.environ.get('DATABASE_PASSWORD')
        self.dbhost = os.environ.get('DATABASE_HOST')
        self.auth_asu = auth.AuthASU(self.dbname, self.dbhost, self.dbuser,
                                     self.dbpass)
        self.asu_requester = other_requests.GetASUAutoID(self.dbname,
                                                         self.dbuser,
                                                         self.dbpass,
                                                         self.dbhost)
        self.asu_photo_uploader = other_requests.PostASUPhoto(self.dbname,
                                                              self.dbuser,
                                                              self.dbpass,
                                                              self.dbhost,
                                                              'send_photo_gross')
        self.asu_photo_uploader_encoded = other_requests.PostASUEncodedPhoto(
            self.dbname,
            self.dbuser,
            self.dbpass,
            self.dbhost,
            'send_photo_gross',
            no_photo_path='test_photo.jpg')

    def test_get_auto_id(self):
        token = self.auth_asu.get_access_token()
        response = self.asu_requester.get_auto_id(car_number='А023НУ702',
                                                  access_token=token)
        self.assertTrue(isinstance(response, int))
        response = self.asu_requester.get_auto_id(car_number='000',
                                                  access_token=token)

    def test_PhotoEncoder(self):
        token = self.auth_asu.get_access_token()
        encoder = other_requests.PhotoEncoder()
        # photo_path = os.path.join(os.path.a, 'test_photo.png')
        photo_path = 'test_photo.jpg'
        obj = encoder.get_encode_photo(photo_path=None,
                                       no_found_photo='test_photo.png')
        response = self.asu_photo_uploader.post_photo(20066, token, obj)
        print(response)

    def test_ActExpanderPhoto(self):
        inst = other_requests.ActExpanderPhoto(self.dbname, self.dbuser,
                                               self.dbpass, self.dbhost)
        act = {}
        inst.expand_act_both(act, 784663, 'test_photo.png')
        print("Act:", act)
