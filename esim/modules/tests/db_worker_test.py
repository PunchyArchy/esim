""" Модуль содержит тесты для класса взаимодействия с БД. """

import unittest
import os
from esim.modules import db_worker


class DBWorkersTest(unittest.TestCase):
    """ Тестирование всех классов. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbname = os.environ.get('DATABASE_NAME')
        self.dbuser = os.environ.get('DATABASE_USERNAME')
        self.dbpass = os.environ.get('DATABASE_PASSWORD')
        self.dbhost = os.environ.get('DATABASE_HOST')
        self.db_polygon_worker = db_worker.DBPolygonWorker(polygon_id=9,
                                                           dbname=self.dbname,
                                                           host=self.dbhost,
                                                           user=self.dbuser,
                                                           password=self.dbpass)
        self.asu_worker = db_worker.DBASUWorker(self.dbname, self.dbuser,
                                                self.dbpass, self.dbhost)

    def test_get_payer_info(self):
        """ Проверка корректности метода на возврат информации о РО. """
        payer_info = self.db_polygon_worker.get_payer_info()
        self.assertTrue(isinstance(payer_info, list))

    def test_get_auto_id(self):
        get_auto_id_method = self.asu_worker.get_endpoint('get_auto_id')
        self.assertEqual(get_auto_id_method, '/extapi/v2/transport/?number={}')

    def test_get_full_endpoint(self):
        response = self.asu_worker.get_full_endpoint('get_auto_id')
        self.assertEqual(response,
                         "https://bashkortostan.asu.big3.ru/extapi/v2/"
                         "transport/?number={}")

    def test_ActPhotoGetter(self):
        inst = db_worker.ActPhotoGetter(self.dbname, self.dbuser, self.dbpass,
                                        self.dbhost)
        photo_path = inst.get_photo(784663, 1)
        print(photo_path)

    def test_get_wserver_id(self):
        inst = db_worker.DBWorker(self.dbname, self.dbuser, self.dbpass,
                                  self.dbhost)
        wserver_id = inst.get_wserver_id(123)
        self.assertEqual(wserver_id, 784663)
