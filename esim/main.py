""" Содержит основной класс для работы """
from abc import ABC, abstractmethod
from esim.modules import auth
from esim.modules import get_acts
from esim.modules import pack_acts
from esim.modules import db_worker
from esim.modules import send_acts
from esim.modules import other_requests


class ESIM(ABC):
    """ ESIM (External System Integration Module), модуль для интеграции
    со сторонними системами и отправки туда данных. (SignAll, АСУ и т.д.)"""

    def __init__(self, ex_sys_name, polygon_id,
                 dbname, dbuser, dbpass, dbhost, *args, **kwargs):
        self.ex_sys_name = ex_sys_name
        self.polygon_id = polygon_id
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbhost = dbhost

    def mainloop(self):
        """
        Основной работа по отправке всех актов.

        :return:
        """
        pass


class ESIMSignall(ESIM, auth.AuthSignall):
    def __init__(self, external_system_name, polygon_id,
                 dbname, dbuser, dbpass, dbhost, *args, **kwargs):
        self.ex_sys_id = 1
        super().__init__(ex_sys_name=external_system_name,
                         polygon_id=polygon_id,
                         dbname=dbname, dbuser=dbuser, dbpass=dbpass,
                         dbhost=dbhost)

    def main(self):
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
        if not acts:
            return
        for act in acts:
            packed = packer.get_packed_act(act)
            wserver_id = photo_expander.get_wserver_id(act['ex_id'])
            photo_expander.expand_act_both(packed, wserver_id, 'test_photo.png')
            sender.send_act(packed, token)


class ESIMASU:
    def __init__(self, polygon_id,
                 dbname, dbuser, dbpass, dbhost, *args, **kwargs):
        self.polygon_id = polygon_id
        self.ex_sys_id = 2
        self.auth_inst = auth.AuthASU(dbname, dbhost, dbuser, dbpass)
        self.getter_inst = get_acts.GetUnsendActsASU(polygon_id, dbname,
                                                     dbuser,
                                                     dbpass, dbhost)
        self.packer_inst = pack_acts.ASUActPacker(polygon_id, dbname, dbuser,
                                                  dbpass, dbhost)
        self.sender_inst = send_acts.SendActASU(dbname, dbuser, dbpass,
                                                dbhost)
        self.gross_photo_sender = other_requests.PostASUEncodedPhoto(dbname,
                                                                     dbuser,
                                                                     dbpass,
                                                                     dbhost,
                                                                     'send_photo_gross',
                                                                     no_photo_path='../modules/tests/test_photo.jpg')
        self.tare_photo_sender = other_requests.PostASUEncodedPhoto(dbname,
                                                                    dbuser,
                                                                    dbpass,
                                                                    dbhost,
                                                                    'send_photo_tare',
                                                                    no_photo_path='../modules/tests/test_photo.jpg')
        self.photo_name_extracter = db_worker.ActPhotoGetter(dbname, dbuser,
                                                             dbpass, dbhost)

    def main(self, acts=None):
        access_token = self.auth_inst.get_access_token()
        acts = self.getter_inst.get_unsend_acts()
        if not acts:
            return
        packed = self.packer_inst.get_packed_acts(acts, access_token)
        for act in packed:
            response = self.sender_inst.send_act(act, access_token)
            gross_photo_path = self.photo_name_extracter.get_photo(act['ext_id'],
                                                                   1)
            tare_photo_path = self.photo_name_extracter.get_photo(act['ext_id'],
                                                                   2)
            response = response.json()
            #response = {'id': 20234, 'ext_id': '128', 'time_arrival': '2021-08-24T13:44:13+05:00', 'time_departure': '2021-08-24T14:33:31+05:00', 'transport_arrival_weight': 5000, 'transport_departure_weight': 3000, 'allow_weight_fault': '1.00', 'transport': {'id': 168, 'name': 'VOLVO_А023НУ702', 'number': 'А023НУ702', 'ext_id_weight': 'А023НУ702', 'average_waste_density': '0.75000', 'ext_id': None, 'author_name': '', 'author_updated_name': None, 'datetime_create': '2020-06-30T16:34:58.456177Z', 'datetime_update': '2021-01-25T13:00:01.573617Z', 'author': 1, 'author_updated': None, '_permissions': [], '__str__': 'VOLVO_А023НУ702'}, 'transport_number_photo': [], 'rfid': 'FFFF000130', 'photos_arrival': [], 'photos_departure': [], 'landfill': {'id': 28, 'address': 'Стерлитамак, Элеваторная, 2А', 'lat': '53.65679', 'lon': '55.95982', 'mun_area': None, 'settlement': None, 'district': None, 'street': None, 'region': None, 'name': 'ООО "Мохит- СТР"', 'ext_id_weight': 'mohit', 'author_name': None, 'author_updated_name': None, 'datetime_create': '2020-02-21T10:54:08.311044Z', 'datetime_update': '2021-07-01T12:01:09.275613Z', 'author': None, 'author_updated': None, '_permissions': [], '__str__': 'Стерлитамак, Элеваторная, 2А'}, 'diff_transport_weight': 2000, 'driver': None, 'density': None, 'waste_volume': None, 'data_source': 'integration', 'determine_volume_method': None, 'reason_lack_weigher': None, 'is_unscheduled': False, 'comment': '', 'is_canceled': False, 'transport_average_waste_density': 0.75, 'author_name': '', 'author_updated_name': None, 'datetime_create': '2021-09-16T12:19:18.377876Z', 'datetime_update': '2021-09-16T12:19:18.446935Z', 'author': 38, 'author_updated': None, '_permissions': [], '__str__': '20234 - 128'}
            self.gross_photo_sender.post(response['id'], gross_photo_path,
                                         access_token,
                                         '../modules/tests/test_photo.jpg')
            self.tare_photo_sender.post(response['id'], tare_photo_path,
                                        access_token,
                                        '../modules/tests/test_photo.jpg')
