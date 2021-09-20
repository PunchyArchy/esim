""" Тесты модуля аутентификации. """

import unittest
from esim.modules import auth


class AuthTest(unittest.TestCase):
    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_extract_auth_endpoint(self):
        """ Тестируем метод извлечения auth endpoint"""
        inst = auth.AuthDb(ex_sys_id=1, dbname='gdb', host='192.168.100.118',
                           user='watchman', password='hect0r1337')
        result = inst.get_auth_endpoint()
        self.assertTrue(isinstance(result, str))
        inst = auth.AuthDb(ex_sys_id=0, dbname='gdb', host='192.168.100.118',
                           user='watchman', password='hect0r1337')
        result_fail = inst.get_auth_endpoint()
        self.assertTrue(not result_fail)

    def test_get_host(self):
        """ Тестируем метод на извлечение главного адреса. """
        inst = auth.AuthDb(ex_sys_id=1, dbname='gdb', host='192.168.100.118',
                           user='watchman', password='hect0r1337')
        result = inst.get_host()
        self.assertTrue(isinstance(result, str))
        inst = auth.AuthDb(ex_sys_id=0, dbname='gdb', host='192.168.100.118',
                           user='watchman', password='hect0r1337')
        result_fail = inst.get_host()
        self.assertTrue(not result_fail)

    def test_get_token(self):
        """ Тестируем получение токена по ID полигона и ID внешней системы. """
        inst = auth.AuthDbToken(polygon_id=9, ex_sys_id=1, dbname='gdb',
                                host='192.168.100.118', user='watchman',
                                password='hect0r1337')
        token = inst.get_token()
        self.assertTrue(isinstance(token, str))

    def test_get_token_ASU(self):
        inst = auth.AuthASU(dbname='gdb',
                            dbhost='192.168.100.118', dbuser='watchman',
                            dbpass='hect0r1337')
        token = inst.get_access_token()
        print(token)

    def test_auth_signall(self):
        inst = auth.AuthSignall(polygon_id=22, ex_sys_name='SignAll',
                                dbname='gdb',
                                dbhost='192.168.100.118', dbuser='watchman',
                                dbpass='hect0r1337')
        inst.set_auth_data_json()
        response = inst.get_access_token()
        print('TOKEN', response)
        self.assertTrue(isinstance(response, str))

    def test_AuthDbUserPass(self):
        inst = auth.AuthDbUserPass(polygon_id=9, ex_sys_name='АСУ',
                                   dbname='gdb',
                                   host='192.168.100.118', user='watchman',
                                   dbpassword='hect0r1337')
        response = inst.get_logpass()
        self.assertTrue(isinstance(response, tuple))
        response = inst.get_access_token()
        print("RESPONSE:", response)


if __name__ == '__main__':
    unittest.main()
