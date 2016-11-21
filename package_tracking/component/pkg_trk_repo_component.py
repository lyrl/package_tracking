#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
from abc import ABCMeta, abstractmethod
import peewee

import util
import package_tracking.component.model as model

logger = util.get_logger("PackageTrackingRecord")


class PkgTrkRepoComponent:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def new_pkg_trk_rec(self, qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no):
        pass

    @abstractmethod
    def new_trk_log(self, package_tracking_obj, tracking_no, update_time, tracking_msg):
        pass


class PkgTrkRepoComponentImpl(PkgTrkRepoComponent):
    def __init__(self, db_path, create_table=False):
        """
        pkgtrk 数据库访问层
        暂支持sqlite3

        Args:
            db_path (str): sqlite3数据库文件路径 eg: /root/sqlite3.db
            create_table (bool): 是否需要自动创建表
        """

        model.deferred_db.init(db_path)

        try:
            model.deferred_db.connect()
        except Exception as e:
            raise PkgTrkRepoException(u'数据库连接失败: ' + e.message)

        if create_table:
            model.PackageTrackingRecord.create_table()
            model.PackageTrackingDetail.create_table()

    def new_pkg_trk_rec(self, qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no):
        """
        创建新的包裹查询订阅记录

        Args:
            qq_nike_name (str): 订阅者qq昵称
            qq_no (str): 订阅者qq号
            qq_group_no (str): 订阅者所在群号
            qq_group_name (str): 订阅者所在群名
            tracking_no (str): 快递单号、包裹单号
        Returns:
            model.PackageTrackingRecord: 跟踪记录
        """
        pkg_track_info = model.PackageTrackingRecord()
        pkg_track_info.qq_nick_name = qq_nike_name
        pkg_track_info.qq_no = qq_no
        pkg_track_info.qq_group_no = qq_group_no
        pkg_track_info.qq_group_name = qq_group_name
        pkg_track_info.tracking_no = tracking_no
        pkg_track_info.update_time = datetime.datetime.now()
        pkg_track_info.package_status = model.STAUS_WAIT_TAKING

        pkg_track_info.save()

        try:
            pkg_track_info.save()
        except Exception as e:
            logger.error("[数据库访问] - 保存包裹订阅信息失败 %s qq:%s tracking_no:%s" % (e.message, str(qq_no), str(tracking_no)))
            raise PkgTrkRepoException("[数据库访问] - 保存包裹订阅信息失败")

        logger.debug("[数据库访问] - 保存包裹订阅信息成功 id:%s" % pkg_track_info.id)

        return pkg_track_info

    def new_trk_log(self, package_tracking_obj, tracking_no, update_time, tracking_msg):
        """
        保存快递单跟踪信息

        Args:
            package_tracking_obj (model.PackageTrackingRecord): 包裹订阅记录
            tracking_no (str): 快递单号、包裹单号
            update_time (datetime): 更新时间
            update_time_int (int): 更新时间戳
            tracking_msg (str): 更新信息

        Returns:
            model.PackageTrackingDetail: 跟踪信息
        """

        pkg_track_log = model.PackageTrackingDetail()

        pkg_track_log.package_tracking = package_tracking_obj
        pkg_track_log.traking_no = tracking_no
        pkg_track_log.tracking_msg = tracking_msg
        pkg_track_log.update_time = update_time

        try:
            pkg_track_log.save()
        except Exception as e:
            logger.error("[数据库访问] - 保存快递更新记录失败 %s 快递单号:%s" % (e.message, str(tracking_no)))
            raise PkgTrkRepoException("[数据库访问] - 保存快递更新记录失败!")

        logger.debug("[数据库访问] - 保存快递更新记录成功! 快递单号:%s" % (str(tracking_no)))

        return pkg_track_log

    def list_all_package_tracking(self):
        """
        列出所有订阅的包裹
        """
        return model.PackageTrackingRecord.select()

    def list_all_in_transiting_pkg(self):
        """
        列出所有未签收的包裹
        """
        return model.PackageTrackingRecord.select().where(model.PackageTrackingRecord.package_status < 3)

    def query(self, qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no):
        """
        根据订阅者查询，如果有数据返回则不需要再次订阅


        Args:
            qq_nike_name (str): qq昵称
            qq_no (str): qq号码
            qq_group_no (str): qq群号
            qq_group_name (str): qq群名称
            tracking_no (str): 快递单号

        Returns:
            peewee.SelectQuery: 结果集
        """

        return model.PackageTrackingRecord.select().where(
            (model.PackageTrackingRecord.qq_nick_name == str(qq_nike_name)) &
            (model.PackageTrackingRecord.qq_no == str(qq_no)) &
            (model.PackageTrackingRecord.qq_group_no == str(qq_group_no)) &
            (model.PackageTrackingRecord.qq_group_name == str(qq_group_name)) &
            (model.PackageTrackingRecord.tracking_no == str(tracking_no))
            # &
            # (model.PackageTrackingRecord.package_status != model.STAUS_IN_DELIVERED)
        )


class PkgTrkRepoException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message



