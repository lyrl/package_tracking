#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import urllib
import urllib2
from abc import ABCMeta, abstractmethod

import util

logger = util.get_logger("MoJoWX")

# api 地址
# https://github.com/sjdy521/Mojo-Weixin/blob/master/doc/Weixin.pod


class MoJoWXComponent:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def send_msg(self, account, msg):
        pass

    @abstractmethod
    def send_group_msg(self,group_name, group_id, msg, mention):
        pass


class MoJoWXComponentImpl(MoJoWXComponent):
    def __init__(self, mojo_host='127.0.0.1', mojo_port='3000'):
        """
        MoJoWX webqq的perl实现可以使用它发送、接收qq消息

        Args:
            mojo_host (str): MoJoWX 主机地址
            mojo_host (str): MoJoWX 服务端口
        """
        self.mojo_host = mojo_host
        self.mojo_port = mojo_port
        self.mojo_url = 'http://%s:%s' % (self.mojo_host, self.mojo_port)

    def send_msg(self, account, msg):
        """
        发送微信私人消息

        Args:
            group_no (str): 好友账号
            msg (str): 消息
        Returns:
            str: json
        """
        service_path = '/openwx/send_friend_message'

        logger.debug("[MoJoWX] - 发送消息给 %s 消息：%s" % (account, msg))

        encoded_data = urllib.urlencode({
            'account': account,
            'content': msg
        })

        try:
            resp = urllib2.urlopen(self.mojo_url + service_path, encoded_data, timeout=10).read()
            logger.debug("[MoJoWX] - 返回信息 %s " % resp)
        except Exception as e:
            logger.error("[MoJoWX] - 发送微信消息失败 %s " % e.message)

    def send_group_msg(self, group_name, group_id, msg, mention):
        """
        发送qq群组消息

        Args:
            group_id (str): 微信群组ID
            group_name (str): 微信群组名
            msg (str): 消息
            mention (str): 需要提到的人
        Returns:
            str: json
        """
        service_path = '/openwx/send_group_message'

        logger.debug("[MoJoWX] - 发送消息到 微信讨论组  %s 消息：%s 提到的人: %s " % (group_name.encode('utf-8'), msg.encode('utf-8'), mention.encode('utf-8')))

        encoded_data = urllib.urlencode({
            'id': group_id,
            'content': '@'+mention+' '+msg if mention else msg
        })

        try:
            resp = urllib2.urlopen(self.mojo_url + service_path, encoded_data, timeout=10).read()
            logger.debug("[MoJoWX] - 返回信息 %s " % resp)
        except Exception as e:
            logger.error("[MoJoWX] - 发送微信群组消息失败 %s " % e.message)


class MoJoWXComponentException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

