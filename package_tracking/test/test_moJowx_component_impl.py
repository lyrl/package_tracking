#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
from unittest import TestCase
from package_tracking.component.mojo_wx import MoJoWXComponentImpl


class TestMoJoWXComponentImpl(TestCase):
    def test_send_msg(self):
        mojo_wx = MoJoWXComponentImpl('103.205.8.130')
        mojo_wx.send_msg('ziyuzan124', '你好')

    def test_send_group_msg(self):
        self.fail()
