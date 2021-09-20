""" Модуль содержит классы для аутентифкации во внешней системе """

from wsqluse import wsqluse
from esim.modules.logger import Logger
from esim.modules.db_worker import DBOperationWorker
from esim.modules.db_worker import DBPolygonWorker
from esim.modules.db_worker import DBExternalSystemWorker
import requests
from abc import ABC


class Auth(ABC):
    """ Класс для аутентификации на стороннем ресурсе """

    def auth(self, *args, **kwargs):
        """
        Отправить команду на авторизацию, вернуть ответ от системы.

        :return: ответ внешней системы.
        """
        response = requests.post(*args, **kwargs)
        return response


class AuthDb(ABC, DBOperationWorker):
    """ Родительский класс, взаимодействующий с БД при работе
    по аутентификации """

    def __init__(self, *args, **kwargs):
        super().__init__(operation_name='auth', *args, **kwargs)

    def get_auth_endpoint(self):
        """ Вернуть ссылку на аутентификацию. """
        return self.get_endpoint(name='auth')

    def get_send_act_endpoint(self):
        """ Вернуть ссылку на отправку акта. """
        return self.get_endpoint(name='send_act')

    def get_full_auth_path(self):
        """ Вернуть полный путь для аутентификации. """
        host = self.get_host()
        auth = self.get_auth_endpoint()
        full_auth = host + auth
        return full_auth


class AuthDbToken(Auth, AuthDb, DBPolygonWorker):
    """ Класс взаимодействующий с БД при работе по аутентификации по токену
    полигона"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @wsqluse.tryExecuteGetStripper
    def get_token(self):
        """
        Вернуть токен внешней системы.

        :return: токен в виде строки.
        """
        command = "SELECT token FROM external_systems_tokens " \
                  "WHERE id=(SELECT token FROM external_systems_affiliation " \
                  "WHERE polygon={} AND external_system={})".format(
            self.polygon_id, self.ex_sys_id)
        return self.try_execute_get(command)


class GetAccessToken(AuthDbToken, Logger):
    def __init__(self, auth_data_json, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_data_json = auth_data_json

    def get_access_token(self):
        """
        Аутентифицироваться по токену.

        :return:
        """
        full_auth = self.get_full_auth_path()
        response = self.auth(full_auth, json=self.auth_data_json)
        self.log_event(self.ex_sys_id, 'Авторизация в АСУ', self.operation_id,
                       response.status_code, response.json())
        if response.status_code is 200:
            return response.json()['token']


class AuthSignall(GetAccessToken):
    """ Класс аутентифкации на SignAll."""

    def __init__(self, polygon_id, dbname, dbhost, dbuser, dbpass,
                 ex_sys_name='SignAll'):
        super().__init__(polygon_id=polygon_id, ex_sys_name=ex_sys_name,
                         dbname=dbname, host=dbhost, user=dbuser,
                         password=dbpass, auth_data_json=None)

    def set_auth_data_json(self):
        token = self.get_token()
        self.auth_data_json = {'refresh_token': token}


class AuthDbUserPass(GetAccessToken):
    """
    Аутентификация во внешней системе через логин и пароль.
    """

    def __init__(self, polygon_id, ex_sys_name, dbname, host, user,
                 dbpassword, *args, **kwargs):
        super(AuthDbUserPass, self).__init__(polygon_id=polygon_id,
                                             ex_sys_name=ex_sys_name,
                                             dbname=dbname, host=host,
                                             user=user, password=dbpassword,
                                             auth_data_json=None)
        login, password = self.get_logpass()
        self.auth_data_json = {'username': login, 'password': password}

    def get_logpass(self):
        """ Получить логин и пароль """
        command = "SELECT login, password FROM external_systems_logpass " \
                  "WHERE external_system={}".format(self.ex_sys_id)
        log_pass = self.try_execute_get(command)
        if log_pass:
            return log_pass[0][0], log_pass[0][1]


class AuthASU(AuthDbUserPass):
    def __init__(self, dbname, dbhost, dbuser, dbpass):
        super(AuthASU, self).__init__(polygon_id=0, ex_sys_name='АСУ',
                                      dbname=dbname, host=dbhost,
                                      user=dbuser, dbpassword=dbpass)
