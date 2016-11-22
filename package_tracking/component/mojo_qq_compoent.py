#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
import urllib
import urllib2
from abc import ABCMeta, abstractmethod

import util
import package_tracking.component.model as model

logger = util.get_logger("MoJoQQ")

# api 地址
# https://github.com/sjdy521/Mojo-Webqq/blob/master/API.md


class MoJoQQComponent:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def send_qq_msg(self, qq_no, msg):
        pass

    @abstractmethod
    def send_group_msg(self, group_no, msg, mention):
        pass

    @abstractmethod
    def send_discuss_group_msg(self, discuss_id, msg, mention):
        pass


class MoJoQQComponentImpl(MoJoQQComponent):
    def __init__(self, mojo_host='127.0.0.1', mojo_port='5000'):
        """
        MojoQQ webqq的perl实现可以使用它发送、接收qq消息

        Args:
            mojo_host (str): mojoqq 主机地址
            mojo_host (str): mojoqq 服务端口
        """
        self.mojo_host = mojo_host
        self.mojo_port = mojo_port
        self.mojo_url = 'http://%s:%s' % (self.mojo_host, self.mojo_port)

    def send_qq_msg(self, qq_no, msg):
        """
        发送qq好友信息

        Args:
            qq_no (str): qq号
            msg (str): 消息
        Returns:
            str: json
        """
        service_path = '/openqq/send_message'
        logger.debug("[MoJoQQ] - 发送消息到 qq %s 消息：%s " % (qq_no, msg))

        encoded_data = urllib.urlencode({
            'qq': qq_no,
            'content': msg
        })
        try:
            resp = urllib2.urlopen(self.mojo_url + service_path, encoded_data, timeout=10).read()
            logger.debug("[MoJoQQ] - 返回信息 %s " % resp)
        except Exception as e:
            logger.error("[MoJoQQ] - 发送私人消息失败!")

    def send_group_msg(self, group_no, msg, mention):
        """
        发送qq群组消息

        Args:
            group_no (str): qq群号
            msg (str): 消息
            mention (str): 需要提到的人
        Returns:
            str: json
        """
        service_path = '/openqq/send_group_message'

        logger.debug("[MoJoQQ] - 发送消息到 qq群 %s 消息：%s 提到的人: %s " % (group_no, msg, mention))

        encoded_data = urllib.urlencode({
            'gnumber': group_no,
            'content': '@'+mention+' '+msg if mention else msg
        })

        try:
            resp = urllib2.urlopen(self.mojo_url + service_path, encoded_data, timeout=10).read()
            logger.debug("[MoJoQQ] - 返回信息 %s " % resp)
        except Exception as e:
            logger.error("[MoJoQQ] - 发送qq消息失败 %s " % e.message)

    def send_discuss_group_msg(self, discuss_id, msg, mention):
        """
        发送qq讨论组消息

        Args:
            discuss_id (str): 讨论组id
            msg (str): 消息
            mention (str): 需要提到的人
        Returns:
            str: json
        """
        service_path = '/openqq/send_discuss_message'

        logger.debug("[MoJoQQ] - 发送消息到 qq讨论组 %s 消息：%s 提到的人: %s".encode('utf-8') % (discuss_id, msg, mention))

        encoded_data = urllib.urlencode({
            'did': discuss_id,
            'content': '@' + mention + ' ' + msg if mention else msg
        })

        try:
            resp = urllib2.urlopen(self.mojo_url + service_path, encoded_data, timeout=10).read()
            logger.debug("[MoJoQQ] - 返回信息 %s " % resp)
        except Exception as e:
            logger.error("[MoJoQQ] - 发送讨论组信息失败!")


class MoJoQQException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

