""" Модуль содержит инструментарий для отправки акта """

import requests
import json
from wsqluse import wsqluse
from esim.modules import logger
from esim.modules.db_worker import DBOperationWorker
from esim.modules.db_worker import DBPolygonWorker
from esim.modules.db_worker import DBExternalSystemWorker
from abc import ABC, abstractmethod
from esim.modules import get_acts


class SendAct(DBOperationWorker):
    """ Класс, отправляющий акты во внешнюю ситсему. """

    def __init__(self, dbname, dbuser, dbpass, dbhost, ex_sys_name, **kwargs):
        super(SendAct, self).__init__(user=dbuser, password=dbpass,
                                      dbname=dbname, host=dbhost,
                                      operation_name='send_act',
                                      ex_sys_name=ex_sys_name)

    @abstractmethod
    def send_act(self, *args, **kwargs):
        pass

    def get_act_send_endpoint(self):
        """
        Вернуть путь, по которому отправить акт.

        :return:
        """
        return self.get_full_endpoint('send_act')


class SendActSignall(SendAct):
    """ Отправить акты в SignAll. """

    def __init__(self, dbname, dbuser, dbpass, dbhost):
        super(SendActSignall, self).__init__(dbname, dbuser, dbpass, dbhost,
                                             ex_sys_name='SignAll')
        self.logger = logger.SendActLogger(dbname, dbuser, dbpass, dbhost,
                                           'SignAll')

    def send_act(self, act, access_token):
        """
        Отправить акт в сигналл.

        :param endpoint:
        :param act:
        :param access_token:
        :return:
        """
        data = json.dumps(act)
        endpoint = self.get_full_endpoint(self.operation_name)
        headers = {"Authorization": "Bearer {}".format(access_token),
                   "Content-Type": "application/json"}
        response = requests.post(endpoint, data=data, headers=headers)
        self.logger.log_act_send(act['number'])
        self.logger.log_event('Отправка акта {} в SignAll'.format(
            self.get_wserver_id(act['number']),
            status_code=response.status_code,
            response=response.json()))
        self.logger.log_act_get(act['number'])
        return response


class SendActASU(SendAct):
    """ Отправить акты в АСУ"""

    def __init__(self, dbname, dbuser, dbpass, dbhost):
        super(SendActASU, self).__init__(dbname=dbname, dbuser=dbuser,
                                         dbpass=dbpass, dbhost=dbhost,
                                         ex_sys_name='АСУ')
        self.logger = logger.SendActLogger(dbname=dbname, dbuser=dbuser,
                                           dbpass=dbpass, dbhost=dbhost,
                                           ex_sys_name='АСУ')

    def send_act(self, act, access_token):
        # Send act to SignAll
        endpoint = self.get_act_send_endpoint()
        data = json.dumps(act)
        headers = {"Authorization": "Token {}".format(access_token),
                   "Content-Type": "application/json"}
        self.logger.log_act_send(act['ext_id'])
        response = requests.post(endpoint, data=data, headers=headers)
        self.logger.log_event('Отправка акта {} в АСУ'.format(act['ext_id']),
                              status_code=response.status_code,
                              response=response.json())
        self.logger.log_act_get(act['ext_id'])
        return response
