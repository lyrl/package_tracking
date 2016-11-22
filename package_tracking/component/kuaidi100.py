#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import urllib
import urllib2
from abc import ABCMeta, abstractmethod

import util

logger = util.get_logger("Kuaidi100")


class Kuaidi100Component:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def query_trk_detail(self, trk_no):
        pass


class Kuaidi100ComponentImpl(Kuaidi100Component):
    def __init__(self):
        """
        快递100查询接口实现
        """

    def query_trk_detail(self, trk_no):
        """
        查询快递跟踪信息

        Args:
            trk_no (str): 快递单号
        Returns:
            str: json
        """

        trk_qry_api = 'https://sp0.baidu.com/9_Q4sjW91Qh3otqbppnN2DJv/pae/channel/data/asyncqury'

        opener = urllib2.build_opener()
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'),
            ('Cookie', 'BAIDUID=69B6916EE6792F0104B440DA366D541E:FG=1')
        ]
        encoded_data = urllib.urlencode({
            'appid': 4001,
            'nu': trk_no
        })

        try:
            resp = opener.open(trk_qry_api, encoded_data, timeout=10).read()
            logger.debug("[Kuaidi100] - 返回信息 %s " % resp)
            return json.loads(resp)
        except Exception as e:
            return None


class Kuaidi100ComponentException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


