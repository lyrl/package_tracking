#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
import peewee
deferred_db = peewee.SqliteDatabase(None)

STAUS_WAIT_TAKING = 0  # 待揽件
STAUS_IN_TRANSIT = 1  # 运输中
STAUS_IN_DELIVERING = 2  # 派件中
STAUS_IN_DELIVERED = 3  # 已签收


class BaseModel(peewee.Model):
    class Meta:
        database = deferred_db


class PackageTrackingRecord(BaseModel):
    # 订阅类型 群、私人信息 group friend
    sub_type = peewee.CharField(null=False)
    # 订阅来源 微信、QQ   wx qq
    sub_source = peewee.CharField(null=False)
    # 群组名
    group_name = peewee.CharField(null=True)
    # 群组号码
    group_no = peewee.CharField(null=True)
    # 订阅者账号
    suber_account = peewee.CharField(null=False)
    # 订阅者昵称
    suber_nike_name = peewee.CharField(null=False)
    # 包裹号码
    tracking_no = peewee.CharField(null=True)
    # 快递公司名称
    company_name = peewee.CharField(null=True)
    # 当前状态 0 待揽收 1 运输中 2 派送中 3 已签收
    package_status = peewee.IntegerField(null=False, default=0)

    # 创建时间
    create_time = peewee.DateTimeField(null=False, default=datetime.datetime.now())
    # 更新时间
    update_time = peewee.DateTimeField(null=False)


class PackageTrackingDetail(BaseModel):
    package_tracking = peewee.ForeignKeyField(PackageTrackingRecord, related_name='logs')
    package_tracking_no = peewee.CharField(null=True)
    tracking_msg = peewee.CharField(null=True)
    update_time = peewee.DateTimeField(null=False)
    update_time_int = peewee.IntegerField(null=False)