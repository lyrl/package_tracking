#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
from abc import ABCMeta, abstractmethod
import peewee
import model
import util
logger = util.get_logger("PackageTrackingRecord")


class PackageTrackingRepoComponent:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def save_new_package_tracking_record(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no):
        pass

    @abstractmethod
    def save_new_tracking_log(self, package_tracking_obj, tracking_no, update_time, tracking_msg, update_time_int):
        pass


class PackageTrackingRepoComponentImpl(PackageTrackingRepoComponent):
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
            raise PackageTrackingRepoComponentException('数据库连接失败: ' + e.message)

        if create_table:
            if not model.PackageTrackingRecord.table_exists():
                model.PackageTrackingRecord.create_table()
            if not model.PackageTrackingDetail.table_exists():
                model.PackageTrackingDetail.create_table()

    def save_new_package_tracking_record(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no):
        """
        创建新的包裹查询订阅记录

        Args:
            suber_account (str): 订阅者账号
            suber_nike_name (str): 订阅者昵称
            group_name (str): 群组名
            group_no (str): 群组号
            sub_type (str): 私人信息，群组信息
            sub_source (str): 订阅来源 qq wx
            tracking_no (str): 快递单号
        Returns:
            model.PackageTrackingRecord: 跟踪记录
        """
        pkg_track_info = model.PackageTrackingRecord()

        pkg_track_info.suber_account = suber_account
        pkg_track_info.suber_nike_name = suber_nike_name
        pkg_track_info.group_name = group_name
        pkg_track_info.group_no = group_no
        pkg_track_info.sub_type = sub_type
        pkg_track_info.sub_source = sub_source
        pkg_track_info.tracking_no = tracking_no

        pkg_track_info.update_time = datetime.datetime.now()
        pkg_track_info.package_status = model.STAUS_WAIT_TAKING

        pkg_track_info.save()

        try:
            pkg_track_info.save()
        except Exception as e:
            logger.error("[数据库访问] - 保存包裹订阅信息失败 %s account:%s tracking_no:%s" % (e.message, str(suber_account), str(tracking_no)))
            raise PackageTrackingRepoComponentException("[数据库访问] - 保存包裹订阅信息失败")

        logger.debug("[数据库访问] - 保存包裹订阅信息成功 id:%s" % pkg_track_info.id)
        return pkg_track_info

    def save_new_tracking_log(self, package_tracking_obj, tracking_no, update_time, tracking_msg, update_time_int):
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
        pkg_track_log.package_tracking_no = tracking_no
        pkg_track_log.tracking_msg = tracking_msg
        pkg_track_log.update_time = update_time
        pkg_track_log.update_time_int = update_time_int

        try:
            pkg_track_log.save()
        except Exception as e:
            logger.error("[数据库访问] - 保存快递更新记录失败 %s 快递单号:%s" % (e.message, str(tracking_no)))
            raise PackageTrackingRepoComponentException("[数据库访问] - 保存快递更新记录失败!")

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

    def query(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no):
        """
        根据订阅者查询，如果有数据返回则不需要再次订阅


        Args:
            suber_account (str): 订阅者账号
            suber_nike_name (str): 订阅者昵称
            group_name (str): 群组名
            group_no (str): 群组号
            sub_type (str): 私人信息，群组信息
            sub_source (str): 订阅来源 qq wx
            tracking_no (str): 快递单号
        Returns:
            peewee.SelectQuery: 结果集
        """

        if sub_type == 'group':

            if sub_source == 'wx':
                return model.PackageTrackingRecord.select().where(
                    (model.PackageTrackingRecord.suber_nike_name == str(suber_nike_name)) &
                    (model.PackageTrackingRecord.group_name == str(group_name)) &
                    (model.PackageTrackingRecord.group_no == str(group_no)) &
                    (model.PackageTrackingRecord.sub_type == str(sub_type)) &
                    (model.PackageTrackingRecord.sub_source == str(sub_source)) &
                    (model.PackageTrackingRecord.tracking_no == str(tracking_no)) &
                    (model.PackageTrackingRecord.package_status != model.STAUS_IN_DELIVERED)
                )
            else:
                return model.PackageTrackingRecord.select().where(
                    (model.PackageTrackingRecord.suber_account == str(suber_account)) &
                    (model.PackageTrackingRecord.suber_nike_name == str(suber_nike_name)) &
                    (model.PackageTrackingRecord.group_name == str(group_name)) &
                    (model.PackageTrackingRecord.group_no == str(group_no)) &
                    (model.PackageTrackingRecord.sub_type == str(sub_type)) &
                    (model.PackageTrackingRecord.sub_source == str(sub_source)) &
                    (model.PackageTrackingRecord.tracking_no == str(tracking_no)) &
                    (model.PackageTrackingRecord.package_status != model.STAUS_IN_DELIVERED)
                )
        else:
            return model.PackageTrackingRecord.select().where(
                (model.PackageTrackingRecord.suber_account == str(suber_account)) &
                (model.PackageTrackingRecord.suber_nike_name == str(suber_nike_name)) &
                (model.PackageTrackingRecord.sub_type == str(sub_type)) &
                (model.PackageTrackingRecord.sub_source == str(sub_source)) &
                (model.PackageTrackingRecord.tracking_no == str(tracking_no)) &
                (model.PackageTrackingRecord.package_status != model.STAUS_IN_DELIVERED)
            )


class PackageTrackingRepoComponentException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message



