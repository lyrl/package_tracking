import json
from unittest import TestCase

import datetime

import package_tracking.component.kuaidi100 as kuaidi100cmpt


class TestKuaidi100ComponentImpl(TestCase):
    def test_query_trk_detail(self):
        kuaidi100 = kuaidi100cmpt.Kuaidi100ComponentImpl()
        resp = kuaidi100.query_trk_detail('883112375650381707')


        logs = resp['data']['info']['context']

        for i in logs[:3]:
            time = datetime.datetime.fromtimestamp(float(i['time']))
            print time.strftime("%Y-%m-%d %H:%M:%S"), i['desc']
