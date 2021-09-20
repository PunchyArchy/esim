""" Тестирование логгера """

import unittest
import os
from esim.modules import logger


class LoggerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dbname = os.environ.get('DATABASE_NAME')
        dbuser = os.environ.get('DATABASE_USERNAME')
        dbpass = os.environ.get('DATABASE_PASSWORD')
        dbhost = os.environ.get('DATABASE_HOST')
        self.logger_object = logger.Logger(dbname=dbname, user=dbuser,
                                           password=dbpass,
                                           host=dbhost)
        self.asu_logger = logger.ASULogger(dbname, dbuser, dbpass, dbhost)
        self.send_act_logger = logger.SendActLogger(dbname, dbuser,
                                                    dbpass, dbhost, 'АСУ')


    def test_log_event(self):
        response = self.logger_object.log_event(ex_sys_id=1,
                                                event_text='TEST EVENT')
        self.assertTrue(response['status'] and
                        isinstance(response['info'], int))

    def test_asu_logger(self):
        self.asu_logger.log_event('TEST')

    def test_SendActLogger(self):
        self.send_act_logger.log_event("TESST_TEXT", 200, "RESPONSE_TEST")

    def test_logactsend(self):
        self.send_act_logger.log_act_send(784663)
        self.send_act_logger.log_act_get(784663)


if __name__ == '__unittest__':
    unittest.main()
