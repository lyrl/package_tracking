#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
from unittest import TestCase
import package_tracking.component.mojo_qq_compoent as mojo_component

class TestMoJoQQComponentImpl(TestCase):
    def test_send_qq_msg(self):
        mojo_qq = mojo_component.MoJoQQComponentImpl('192.168.30.130', '5000')
        mojo_qq.send_qq_msg('184387904', 'test')

    def test_send_group_msg(self):
        mojo_qq = mojo_component.MoJoQQComponentImpl('192.168.30.130', '5000')
        mojo_qq.send_group_msg('498880156', '测试@', 'lyrl')

    def test_send_discuss_group_msg(self):
        self.fail()
