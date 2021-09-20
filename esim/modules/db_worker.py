""" Модуль, содержащий класс для работы с базой данных """
from wsqluse import wsqluse


class DBWorker(wsqluse.Wsqluse):
    """ Интерфейс для работы с БД в рамках внешней системы. """

    def __init__(self, dbname, user, password, host,
                 *args, **kwargs):
        super().__init__(dbname, user, password, host)

    @wsqluse.tryExecuteGetStripper
    def get_wserver_id(self, ex_id):
        """
        Вернуть ID record из GDB, согласно его ex_id.

        :param ex_id: ID из AR.
        :return:
        """
        command = "SELECT id FROM records WHERE ex_id={}".format(ex_id)
        return self.try_execute_get(command)


class DBPolygonWorker(DBWorker):
    """ Интерфейс для работы с БД в разрвезе полигона """

    def __init__(self, dbname, user, password, host, polygon_id,
                 *args, **kwargs):
        super().__init__(dbname, user, password, host)
        self.polygon_id = polygon_id
        self.polygon_payer = self.get_payer_info()

    @wsqluse.getTableDictStripper
    def get_payer_info(self):
        """ Вернуть данные о плательщике (РО), который закреплен
        за этим полигоном. """
        command = "with region_table as " \
                  "(SELECT region FROM users WHERE id={}) " \
                  "select * from " \
                  "users, region_table where " \
                  "users.region = region_table.region and role=2".format(
            self.polygon_id)
        info = self.get_table_dict(command)
        return info

    @wsqluse.getTableDictStripper
    def get_polygon_info(self):
        """ Вернуть все данные о полигоне. """
        command = "SELECT * FROM users WHERE id={}".format(self.polygon_id)
        polygon_info = self.get_table_dict(command)
        return polygon_info


class DBExternalSystemWorker(DBWorker):
    """ Интерфейс для работы с БД в разрвезе конкретной внешней системы """

    def __init__(self, dbname, user, password, host,
                 ex_sys_name, *args, **kwargs):
        super().__init__(dbname, user, password, host, *args, **kwargs)
        self.ex_sys_id = self.get_ex_sys_id(ex_sys_name)

    @wsqluse.tryExecuteGetStripper
    def get_host(self):
        """ Вернуть главный HTTP адрес внешней системы. """
        command = "SELECT address FROM external_systems WHERE id={}".format(
            self.ex_sys_id)
        return self.try_execute_get(command)

    @wsqluse.tryExecuteGetStripper
    def get_ex_sys_id(self, name):
        """
        Вернуть ID внешней системе из GDB по его имени.

        :param name: Имя внешней системы.
        :return: ID: int.
        """
        command = "SELECT id FROM external_systems WHERE name='{}'"
        command = command.format(name)
        return self.try_execute_get(command)

    @wsqluse.tryExecuteGetStripper
    def get_endpoint(self, name):
        """
        Вернуть API endpoint внешней системы по ее названию (из БД).

        :param name: Название API-endpoint из
            gdb.external_systems_operation_types.
        :return: dict
        """
        command = "SELECT endpoint FROM external_systems_operations " \
                  "WHERE system={} and " \
                  "type=(SELECT id FROM external_systems_operation_types " \
                  "WHERE name='{}')".format(self.ex_sys_id, name)
        return self.try_execute_get(command)

    def get_full_endpoint(self, name):
        """ Возвращает полный путь API endpoind, вместе с адресом хоста """
        full_endpoint = self.get_host() + self.get_endpoint(name)
        return full_endpoint


class DBSignallWorker(DBExternalSystemWorker):
    """ Класс для работы с БД в рамках внешней системы SignAll """

    def __init__(self, dbname, user, password, host, *args, **kwargs):
        super(DBSignallWorker, self).__init__(dbname, user, password, host,
                                              ex_sys_name='SignAll',
                                              *args, **kwargs)


class DBASUWorker(DBExternalSystemWorker):
    """ Класс для работы с БД в рамках внешней системы SignAll """

    def __init__(self, dbname, user, password, host, *args, **kwargs):
        super(DBASUWorker, self).__init__(dbname, user, password, host,
                                          ex_sys_name='АСУ',
                                          *args, **kwargs)

    @wsqluse.getTableDictStripper
    def get_asu_name(self, polygon_id):
        """ Вернуть данные о полигоне в АСУ. """
        command = "SELECT * FROM asu_poligons WHERE poligon={}".format(
            polygon_id)
        polygon_info = self.get_table_dict(command)
        return polygon_info


class DBOperationWorker(DBExternalSystemWorker):
    """ Интерфейс для работы с базой данных в разрезе операции """

    def __init__(self, dbname, user, password, host, operation_name: str,
                 *args, **kwargs):
        super(DBOperationWorker, self).__init__(dbname, user, password, host,
                                                *args, **kwargs)
        self.operation_id = self.get_operation_id(operation_name)
        self.operation_name = operation_name

    @wsqluse.tryExecuteGetStripper
    def get_operation_id(self, operation_name):
        """
        Вернуть ID операции по его названию.

        :param operation_name: Название операции.
        :return: ID опереции.
        """
        command = "SELECT id FROM external_systems_operation_types " \
                  "WHERE name='{}'".format(operation_name)
        return self.try_execute_get(command)


class ActPhotoGetter(DBWorker):
    def __init__(self, dbname, dbuser, dbpass, dbhost):
        super(ActPhotoGetter, self).__init__(dbname=dbname, user=dbuser,
                                             password=dbpass, host=dbhost)

    @wsqluse.tryExecuteGetStripper
    def get_photo(self, record, photo_type):
        """
        Извлечь фото по его типу и ID заезда.

        :param record: ID записи.
        :param photo_type: Тип фото (братто, тара и т.д)
        :return:
        """
        command = "SELECT photo_path FROM act_photos " \
                  "WHERE record={} and photo_type={}".format(record,
                                                             photo_type)
        return self.try_execute_get(command)
