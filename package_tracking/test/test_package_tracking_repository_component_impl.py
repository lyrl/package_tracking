#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
from unittest import TestCase

import datetime

from peewee import SQL

import package_tracking.component.package_tracking_repo as repo


class TestPackageTrackingRepositoryComponentImpl(TestCase):
    def test_create_new_package_tracking_record(self):
        package_tracking_repo = repo.PackageTrackingRepoComponentImpl('./sqlite3.db', True)

        tracking_info = package_tracking_repo.new_pkg_trk_rec(
            'lyrl',
            '184387904',
            '498880156',
            'Mojo-Webqq',
            '45457874545454'
        )

        package_tracking_repo.new_trk_log(tracking_info, tracking_info.tracking_no, datetime.datetime.now(), None, '已发货')
        package_tracking_repo.new_trk_log(tracking_info, tracking_info.tracking_no, datetime.datetime.now(), None, '已发货')
        package_tracking_repo.new_trk_log(tracking_info, tracking_info.tracking_no, datetime.datetime.now(), None, '已发货')
        package_tracking_repo.new_trk_log(tracking_info, tracking_info.tracking_no, datetime.datetime.now(), None, '已发货')

        logs = tracking_info.logs

        for log in logs:
            print log.traking_no, log.tracking_msg

        all_trakcing = package_tracking_repo.list_all_package_tracking()
        all_trakcing = all_trakcing.order_by(SQL('update_time').desc())


        for i in all_trakcing:
            print i.qq_nick_name, i.qq_no, i.id, i.update_time


    def test_insert_new_tracking_log(self):
        pass