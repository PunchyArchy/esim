""" Модуль содержит инструментарий для получения данных об акте. """
import wsqluse.wsqluse

from esim.modules.db_worker import DBWorker
from esim.modules.db_worker import DBSignallWorker
from esim.modules.db_worker import DBExternalSystemWorker
from esim.modules.db_worker import DBASUWorker


class GetUnsendActs(DBWorker):
    """ Супер класс по получению актов. """

    def __init__(self, dbname, user, password, host, *args, **kwargs):
        super().__init__(dbname, user, password, host)

    def get_unsend_acts_command(self, *args, **kwargs):
        """ Получить все акты, без каких либо фильтров """
        command = "SELECT records.ex_id, records.time_in, records.time_out, " \
                  "trash_cats.name as trash_cat, " \
                  "trash_types.name as trash_type, records.brutto," \
                  "records.cargo, am.name as auto_model, auto.car_number, rm.rfid, " \
                  "companies.inn as carrier_inn, records.tara, trash_types.name " \
                  "FROM records " \
                  "LEFT JOIN trash_cats " \
                  "ON (records.trash_cat = trash_cats.id) " \
                  "LEFT JOIN trash_types " \
                  "ON (records.trash_type = trash_types.id) " \
                  "LEFT JOIN auto ON (records.car = auto.id) " \
                  "LEFT JOIN companies ON (records.carrier = companies.id) " \
                  "LEFT JOIN users ON (records.polygon = users.id) " \
                  "LEFT JOIN rfid_marks rm ON (auto.rfid_id = rm.id) " \
                  "LEFT JOIN auto_models am ON (auto.auto_model = am.id) " \
                  "LEFT JOIN external_systems_acts_sending_control esasc " \
                  " ON records.id = esasc.record"
        return command

    @wsqluse.wsqluse.getTableDictStripper
    def get_unsend_acts(self, command: str = None):
        """
        Испольнить команду по запросу неотправленных актов и вернуть ответ.

        :param command: SQL запрос с фильтрам, если не указан, будет
            использоваться встроенная команда, которая возвращает все акты.
        :return: Список словарей с колонками и значениями колонок.
        """
        if not command:
            command = self.get_unsend_acts_command()
        return self.get_table_dict(command)


class GetUnsendActsFilters(GetUnsendActs):
    """ Вернуть акты добавив фильтры в запрос SQL. """

    def __init__(self, dbname, user, password, host):
        super().__init__(dbname, user, password, host)

    def add_filter(self, sql_request: str, sql_filter: str = None):
        """
        Добавить к запросу фильтр вида WHERE column=value.

        :param sql_request: Фильтр (пробел между фильтром и запросом вставится
            в этой функции автоматически).
        :param sql_request: Оригинальный запрос, если не укзан, будет
            использоваться ответ встроенного метода get_unsend_acts_command.
        :return:
        """

        sql_request = ' '.join((sql_request, sql_filter))
        return sql_request

    def get_unsend_acts_command(self, *args, **kwargs):
        self.get_acts_command = super().get_unsend_acts_command()
        self.get_acts_command = self.add_filter(self.get_acts_command,
                                                self.filters)
        return self.get_acts_command

    def set_filters(self, filters):
        self.filters = filters


class GetUnsendActs(DBSignallWorker, GetUnsendActsFilters):
    def __init__(self, polygon_id, ex_sys_name, dbname, user, password, host):
        super().__init__(dbname, user, password, host)
        filters = "WHERE records.polygon={} and esasc.external_system={} and " \
                  "(trash_cats.name='ТКО-4' or trash_cats.name='ТКО-5') and " \
                  "esasc.must_be_send=True"
        filters = filters.format(polygon_id, self.get_ex_sys_id(ex_sys_name))
        self.set_filters(filters)


class GetUnsendActsSignall(DBSignallWorker, GetUnsendActsFilters):
    def __init__(self, polygon_id, dbname, user, password, host):
        super().__init__(dbname, user, password, host)
        filters = "WHERE records.polygon={} and esasc.external_system={} and " \
                  "(trash_cats.name='ТКО-4' or trash_cats.name='ТКО-5') and " \
                  "esasc.must_be_send=True and esasc.get is null"
        filters = filters.format(polygon_id, self.ex_sys_id)
        self.set_filters(filters)


class GetUnsendActsASU(DBASUWorker, GetUnsendActsFilters):
    def __init__(self, polygon_id, dbname, user, password, host):
        super().__init__(dbname, user, password, host)
        filters = "WHERE records.polygon={} and esasc.external_system={} and " \
                  "(trash_cats.name='ТКО-4' or trash_cats.name='ТКО-5') and " \
                  "esasc.must_be_send=True and esasc.get is null"
        filters = filters.format(polygon_id, self.ex_sys_id)
        self.set_filters(filters)
