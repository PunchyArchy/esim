""" Модуль содержит тесты для всех классов, занимающихся извлечением актов
из БД"""

import unittest
import os
from esim.modules import get_acts
from esim.modules import pack_acts


class GetActsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(GetActsTest, self).__init__(*args, **kwargs)
        self.dbname = os.environ.get('DATABASE_NAME')
        self.dbuser = os.environ.get('DATABASE_USERNAME')
        self.dbpass = os.environ.get('DATABASE_PASSWORD')
        self.dbhost = os.environ.get('DATABASE_HOST')

    def test_GetUnsendActs(self):
        inst = get_acts.GetUnsendActs(dbname=self.dbname,
                                      host=self.dbhost,
                                      user=self.dbuser,
                                      password=self.dbpass)
        response = inst.get_unsend_acts()
        self.assertTrue(len(response) == 3)

    def test_GetUnsendActsSignall(self):
        inst = get_acts.GetUnsendActsSignall(dbname=self.dbname,
                                             host=self.dbhost,
                                             user=self.dbuser,
                                             password=self.dbpass,
                                             polygon_id=9)
        resp = inst.get_unsend_acts()
        common_inst = get_acts.GetUnsendActs(ex_sys_name='SignAll',
                                             dbname=self.dbname,
                                             host=self.dbhost,
                                             user=self.dbuser,
                                             password=self.dbpass,
                                             polygon_id=9)
        common_response = common_inst.get_unsend_acts()
        self.assertEqual(resp, common_response)

    def test_GetUnsendActsASU(self):
        inst = get_acts.GetUnsendActsASU(dbname=self.dbname,
                                         host=self.dbhost,
                                         user=self.dbuser,
                                         password=self.dbpass,
                                         polygon_id=9)
        response = inst.get_unsend_acts()
        self.assertTrue(response[0]['ex_id'] == 128)
        common_inst = get_acts.GetUnsendActs(ex_sys_name='АСУ',
                                             dbname=self.dbname,
                                             host=self.dbhost,
                                             user=self.dbuser,
                                             password=self.dbpass,
                                             polygon_id=9)
        common_response = common_inst.get_unsend_acts()
        self.assertEqual(response, common_response)


if __name__ == '__main__':
    unittest.main()
