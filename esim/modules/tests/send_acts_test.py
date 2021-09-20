""" Тестирование отправки актов в сторонние системы """

import unittest
import os
from esim.modules import auth
from esim.modules import get_acts
from esim.modules import pack_acts
from esim.modules import send_acts
from esim.modules import other_requests


class SendActTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SendActTest, self).__init__(*args, **kwargs)
        self.dbname = os.environ.get('DATABASE_NAME')
        self.dbuser = os.environ.get('DATABASE_USERNAME')
        self.dbpass = os.environ.get('DATABASE_PASSWORD')
        self.dbhost = os.environ.get('DATABASE_HOST')

    def test_asu_send_act(self):
        auth_get = auth.AuthASU(dbname=self.dbname, dbpass=self.dbpass,
                                dbhost=self.dbhost, dbuser=self.dbuser)
        access_token = auth_get.get_access_token()
        acts_getter = get_acts.GetUnsendActsASU(9, self.dbname, self.dbuser,
                                                self.dbpass,
                                                self.dbhost)
        unsend_acts = acts_getter.get_unsend_acts()
        acts_packer = pack_acts.ASUActPacker(9, self.dbname, self.dbuser,
                                             self.dbpass, self.dbhost,)
        print("Unsend acts:", unsend_acts)
        packed_acts = acts_packer.get_packed_acts(unsend_acts, access_token)
        act_sender = send_acts.SendActASU(self.dbname, self.dbuser,
                                          self.dbpass, self.dbhost)
        for act in packed_acts:
            print(act)
            result = act_sender.send_act(act, access_token)
            print("RESULT:", result.json())

    def test_SignallActSender(self):
        packer = pack_acts.SignallActPacker(9, self.dbname, self.dbuser,
                                            self.dbpass,
                                            self.dbhost)
        getter = get_acts.GetUnsendActsSignall(9, self.dbname, self.dbuser,
                                               self.dbpass,
                                               self.dbhost)
        sender = send_acts.SendActSignall(self.dbname, self.dbuser,
                                          self.dbpass, self.dbhost)
        auther = auth.AuthSignall(9, self.dbname, self.dbhost, self.dbuser,
                                  self.dbpass)
        photo_expander = other_requests.ActExpanderPhoto(self.dbname,
                                                         self.dbuser,
                                                         self.dbpass,
                                                         self.dbhost)
        auther.set_auth_data_json()
        token = auther.get_access_token()
        acts = getter.get_unsend_acts()
        print("Get unsend acts:", acts)
        for act in acts:
            packed = packer.get_packed_act(act)
            wserver_id = photo_expander.get_wserver_id(act['ex_id'])
            photo_expander.expand_act_both(packed, wserver_id, 'test_photo.png')
            response = sender.send_act(packed, token)
            if response.status_code == 200:
                print(response.json())
            print(response)
