""" Модуль содержит инструменты для упакования актов в нужный вид,
перед отправкой их во внешние системы. """
import tzlocal
from pytz import timezone
from abc import ABC, abstractmethod
from esim.modules import db_worker
from esim.modules import exceptions
from esim.modules import other_requests


class ActsPacker(ABC):
    @abstractmethod
    def get_packed_acts(self, *args, **kwargs):
        pass


class SignallActPacker(ActsPacker):
    def __init__(self, polygon_id, dbname, user, password, host):
        super(SignallActPacker, self).__init__()
        self.pol_worker = db_worker.DBPolygonWorker(dbname, user, password,
                                                    host,
                                                    polygon_id)
        self.payer_info = self.pol_worker.get_payer_info()[0]

    def format_date(self, date):
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        return date

    def inn_expander(self, inn):
        """ Расширяет inn нулями в начале так, что бы ее длина была = 12"""
        while len(inn) < 12:
            inn = '0' + inn
        return inn

    def get_packed_acts(self, acts):
        """ Возвращает итератор с актами, готовыми к отправке """
        packed_acts = []
        for act_dict in acts:
            packed_act = {}
            packed_act['number'] = act_dict['car_number']
            packed_act['time'] = self.format_date(act_dict['time_in'])
            packed_act['exit_time'] = self.format_date(act_dict['time_out'])
            packed_act['waste_category'] = act_dict['trash_cat']
            packed_act['danger_class'] = act_dict['trash_cat']
            packed_act['gross_weight'] = act_dict['brutto']
            packed_act['net_weight'] = act_dict['cargo']
            packed_act['model_car'] = act_dict['auto_model']
            packed_act['rf_id'] = act_dict['rfid']
            packed_act['transporter_inn'] = self.inn_expander(
                act_dict['carrier_inn'])
            packed_act['payer_inn'] = self.inn_expander(self.payer_info['inn'])
            packed_act['container'] = act_dict['trash_cat']
            packed_act['cargo_type'] = act_dict['trash_type']
            packed_acts.append(packed_act)
        return iter(packed_acts)

    def get_packed_act(self, act_dict):
        """ Возвращает итератор с актами, готовыми к отправке """
        packed_act = {}
        packed_act['number'] = str(act_dict['ex_id'])
        packed_act['time'] = self.format_date(act_dict['time_in'])
        packed_act['exit_time'] = self.format_date(act_dict['time_out'])
        packed_act['waste_category'] = act_dict['trash_cat']
        packed_act['danger_class'] = act_dict['trash_cat']
        packed_act['gross_weight'] = str(act_dict['brutto'])
        packed_act['net_weight'] = str(act_dict['cargo'])
        packed_act['model_car'] = act_dict['auto_model']
        packed_act['state_number_auto'] = act_dict['car_number']
        packed_act['rf_id'] = str(act_dict['rfid'])
        packed_act['transporter_inn'] = self.inn_expander(
            act_dict['carrier_inn'])
        packed_act['payer_inn'] = self.inn_expander(self.payer_info['inn'].strip())
        packed_act['container'] = act_dict['trash_cat']
        packed_act['cargo_type'] = act_dict['trash_type']
        return packed_act


class ASUActPacker(ActsPacker,
                   db_worker.DBPolygonWorker,
                   db_worker.DBASUWorker):
    """
    Пакер актов, отправляемых на сигнал. Возвращает data, готовую для пересылки
    """

    def __init__(self, polygon_id, dbname, user, password, host):
        super().__init__(dbname=dbname, user=user,
                         password=password, host=host,
                         polygon_id=polygon_id)
        self.polygon_info = self.get_polygon_info()
        self.asu_polygon_info = self.get_asu_polygon_info()
        self.auto_request = other_requests.GetASUAutoID(dbname=dbname,
                                                        user=user,
                                                        host=host,
                                                        password=password)

    def get_asu_polygon_info(self, *args, **kwargs):
        result = super(ASUActPacker, self).get_asu_name(self.polygon_id)
        if not result:
            raise exceptions.NoAsuPolygon
        return result[0]

    def format_date_for_asu(self, date):
        print(date, type(date))
        # date = self.set_current_localzone(date)
        # date = self.set_new_timezone(date, new_timezone='GMT')
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        return date

    def set_current_localzone(self, date):
        date = date.replace(tzinfo=None)
        current_localzone = tzlocal.get_localzone()
        date = current_localzone.localize(date)
        return date

    def set_new_timezone(self, date, new_timezone, *args, **kwargs):
        date = date.astimezone(timezone(new_timezone))
        return date

    def get_packed_acts(self, acts, access_token):
        """ Возвращает итератор с актами, готовыми к отправке """
        packed_acts = []
        for act_dict in acts:
            packed_act = {}
            packed_act["ext_id_landfill_weight"] = self.asu_polygon_info[
                'asu_name']
            packed_act["transport"] = self.auto_request.get_auto_id(
                car_number=act_dict['car_number'],
                access_token=access_token)
            packed_act['ext_id_transport_weight'] = act_dict['car_number']
            packed_act['transport_name'] = act_dict['car_number']
            packed_act['transport_number'] = act_dict['car_number']
            packed_act["comment"] = ""
            packed_act['ext_id'] = act_dict['ex_id']
            packed_act['time_arrival'] = self.format_date_for_asu(
                act_dict['time_in'])
            packed_act['time_departure'] = self.format_date_for_asu(
                act_dict['time_out'])
            packed_act['waste_category'] = act_dict['trash_cat']
            packed_act['transport_arrival_weight'] = act_dict['brutto']
            packed_act['transport_departure_weight'] = act_dict['tara']
            packed_act['model_car'] = act_dict['auto_model']
            packed_act['rfid'] = act_dict['rfid']
            packed_acts.append(packed_act)
        return iter(packed_acts)
