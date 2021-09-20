""" Модуль содержит логгер для логирования всех событий, потенциально
возникающих во время взаимодействия с внешней системой. """
import datetime

from wsqluse import wsqluse
from esim.modules.db_worker import DBASUWorker, DBExternalSystemWorker, \
    DBOperationWorker


class Logger(wsqluse.Wsqluse):
    def __int__(self, dbname, dbuser, dbpass, dbhost, *args, **kwargs):
        super().__init__(dbname=dbname, user=dbuser, password=dbpass,
                         host=dbhost)

    @wsqluse.tryExecuteDoubleStripper
    def log_event(self, ex_sys_id: int, event_text: str, operation=None,
                  status_code=None, response=None):
        """
        Логгировать событие.

        :param event_text: Текст события.
        :param operation: ID операции, выполняя которое произошло событие.
        :param ex_sys_id: ID внешней системы.
        :param status_code: HTTP код, который вернула сторонняя система.
        :param response: Полный ответ, который вернула сторонняя система.
        :return: ответ Wsqluse.
        """
        response = str(response)
        command = """INSERT INTO external_systems_log 
                    (external_system, operation, text, status_code, response) 
                    VALUES (%s, %s, %s, %s, %s)"""
        values = (ex_sys_id, operation, event_text, status_code, response)
        return self.try_execute_double(command, values)

    def log_act_send(self, act_id):
        """
        Зафиксировать, что акт был отправлен.

        :param act_id: ID акта.
        :return:
        """

        command = """UPDATE external_systems_acts_sending_control 
                    SET send=%s WHERE 
                    record=(SELECT id FROM records WHERE ex_id=%s)"""
        values = (datetime.datetime.now(), act_id)
        return self.try_execute_double(command, values)

    def log_act_get(self, act_id):
        """
        Зафиксировать, что акт был получен.

        :param act_id: ID акта.
        :return:
        """

        command = """UPDATE external_systems_acts_sending_control 
                    SET get=%s WHERE 
                    record=(SELECT id FROM records WHERE ex_id=%s)"""
        values = (datetime.datetime.now(), act_id)
        return self.try_execute_double(command, values)


class ASULogger(DBASUWorker, Logger):
    def __init__(self, dbname, dbuser, dbpass, dbhost, **kwargs):
        super().__init__(dbname=dbname, user=dbuser, password=dbpass,
                         host=dbhost)

    def log_event(self, event_text: str, operation=None,
                  status_code=None, response=None, *args, **kwargs):
        return super().log_event(self.ex_sys_id, event_text, operation,
                                 status_code, response=response)

    def log_auto_request_result(self, car_number, operation_id, response,
                                event_text, status_code=None):
        """
        Логгировать результат запроса авто из АСУ.

        :return:
        """
        self.log_event(
            event_text=event_text.format(car_number),
            operation=operation_id,
            response=response,
            status_code=status_code
        )


class SendActLogger(DBOperationWorker, Logger):
    """ Логгер логгирующий состояние отправки актов в сторонние системы"""

    def __init__(self, dbname, dbuser, dbpass, dbhost, ex_sys_name, **kwargs):
        super().__init__(dbname=dbname, user=dbuser, password=dbpass,
                         host=dbhost, ex_sys_name=ex_sys_name,
                         operation_name='send_act')

    def log_event(self, event_text: str, status_code=None, response=None,
                  *args, **kwargs):
        super().log_event(ex_sys_id=self.ex_sys_id, event_text=event_text,
                          operation=self.operation_id,
                          status_code=status_code, response=response)
