""" Модуль содержит вспомогательные классы, которые нужны при отправке
актов. Например, класс, запрашивающий из АСУ ID авто по его гос. номеру"""
import requests
import random
import json
import os
import base64
from esim.modules import db_worker
from esim.modules import logger


class GetASUAutoID(db_worker.DBOperationWorker, logger.ASULogger,
                   db_worker.DBASUWorker):
    def __init__(self, *args, **kwargs):
        super(GetASUAutoID, self).__init__(operation_name='get_auto_id',
                                           *args, **kwargs)

    def get_auto_id(self, car_number, access_token):
        """
        Вернуть ID auto из СУБД АСУ.

        :param car_number: Гос. номер, по которому идет поиск.
        :param access_token: Токен для обращения в restAPI.
        :return: Либо ID, либо, если такого авто нет, рандомное значение
            в пределах определенного диапазона.
        """
        get_auto_method = self.get_full_endpoint('get_auto_id')
        get_auto_request = get_auto_method.format(car_number)
        headers = {"Authorization": "Token {}".format(access_token),
                   "Content-Type": "application/json"}
        response = requests.get(get_auto_request, headers=headers)
        try:
            car_id = response.json()['results'][0]['id']
            event_text = 'Авто с гос.номером {} найдено'
        except IndexError:
            car_id = random.randrange(176, 189)
            event_text = 'Авто с гос.номером {} не найдено'
        self.log_auto_request_result(car_number,
                                     self.operation_id,
                                     response.json(), event_text=event_text,
                                     status_code=response.status_code)
        return car_id


class PostASUPhoto(db_worker.DBOperationWorker, logger.ASULogger,
                   db_worker.DBASUWorker):
    def __init__(self, dbname, dbuser, dbpass, dbhost, operation_name,
                 **kwargs):
        super().__init__(operation_name=operation_name, dbname=dbname,
                         user=dbuser, password=dbpass, host=dbhost,
                         ex_sys_name='АСУ')

    def post_photo(self, act_id, access_token, photoobj):
        """
        Разместить фотографию заезда.

        :param act_id: ID акта из АСУ, к которому релевантна фотография.
        :param access_token: токен для доступа к API.
        :param photoobj: Фото.
        :return:
        """
        post_photo_endpoint = self.get_full_endpoint(self.operation_name)
        post_photo_request = post_photo_endpoint.format(act_id)
        data = {"file": photoobj}
        data = json.dumps(data)
        headers = {"Authorization": "Token {}".format(access_token),
                   "Content-Type": "application/json"}
        response = requests.post(post_photo_request, data=data,
                                 headers=headers)
        self.log_event('Выгрузка фото для акта {}'.format(act_id),
                       self.operation_id,
                       response.status_code,
                       response.json())
        return response


class PhotoEncoder:
    """Класс, который кодирует фото в кодировку, готовую к высылке во
    внешнюю систему """

    def get_encode_photo(self, photo_path, no_found_photo):
        if not photo_path or not os.path.exists(photo_path):
            photo_path = no_found_photo
        with open(photo_path, 'rb') as image_file:
            encoded_string = self.encode_photo(image_file)
        return encoded_string

    def encode_photo(self, image_file, last_truncate=1):
        encoded_string = base64.b64encode(image_file.read())
        encoded_string = str(encoded_string).replace("b'", '')
        encoded_string = encoded_string[:-last_truncate]
        return encoded_string


class PhotoEncoderSignall(PhotoEncoder):
    """ Класс, который кодирует фото в кодировку, готовую к высылке в SignAll
    """
    def encode_photo(self, image_file, **kwargs):
        return super().encode_photo(image_file, last_truncate=1)


class PostASUEncodedPhoto(PostASUPhoto, PhotoEncoder):
    """
    Кодирует фото в base64 и отправляет ее
    """
    def __init__(self, dbname, dbuser, dbpass, dbhost, operation_name,
                 no_photo_path, **kwargs):
        self.no_found_photo = no_photo_path
        super(PostASUEncodedPhoto, self).__init__(dbname, dbuser, dbpass,
                                                  dbhost, operation_name,
                                                  no_found_photo=no_photo_path)

    def post(self, act_id, photo_path, access_token, no_found_photo):
        encoded = self.get_encode_photo(photo_path, no_found_photo)
        return self.post_photo(act_id, access_token, encoded)


class ActExpanderPhoto(PhotoEncoder, db_worker.ActPhotoGetter):
    """ Класс, расширяющий акт фотографиями """
    def expand_act(self, act: dict, key_name: str, photo_obj: str):
        expand = {key_name:photo_obj}
        act.update(expand)
        return act

    def expand_act_both(self, act, record_id, no_found_photo):
        gross_photo = self.get_photo(record_id, 1)
        tare_photo = self.get_photo(record_id, 2)
        gross_photo_obj = self.get_encode_photo(gross_photo, no_found_photo)
        tare_photo_obj = self.get_encode_photo(tare_photo, no_found_photo)
        self.expand_act(act, 'entry_photo', gross_photo_obj)
        self.expand_act(act, 'exit_photo', tare_photo_obj)

