""" Тесты упаковщиков актов """

import unittest
import os
from esim.modules import pack_acts
from esim.modules import get_acts
from esim.modules import auth


class PackActTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbname = os.environ.get('DATABASE_NAME')
        self.dbuser = os.environ.get('DATABASE_USERNAME')
        self.dbpass = os.environ.get('DATABASE_PASSWORD')
        self.dbhost = os.environ.get('DATABASE_HOST')
        self.asu_auth = auth.AuthASU(self.dbname, self.dbhost, self.dbuser,
                                     self.dbpass)
        self.asu_token = self.asu_auth.get_access_token()

    def test_signall_packer(self):
        """ Тесты упаковщика для сигналла. """
        packer = pack_acts.SignallActPacker(9, self.dbname, self.dbuser,
                                            self.dbpass,
                                            self.dbhost)
        getter = get_acts.GetUnsendActsSignall(9, self.dbname, self.dbuser,
                                               self.dbpass,
                                               self.dbhost)
        acts = getter.get_unsend_acts()
        print("Get unsend acts:", acts)
        res = packer.get_packed_acts(acts)
        for act in res:
            print(act)

    def test_asu_packer(self):
        packer = pack_acts.ASUActPacker(9, self.dbname, self.dbuser,
                                        self.dbpass, self.dbhost,
                                        access_token=self.asu_token)
        getter = get_acts.GetUnsendActsASU(polygon_id=9, dbname=self.dbname,
                                           user=self.dbuser,
                                           password=self.dbpass,
                                           host=self.dbhost)
        acts = getter.get_unsend_acts()
        packed_acts = packer.get_packed_acts(acts)
        print('PACKED ACTS:')
        for act in packed_acts:
            print(act)

