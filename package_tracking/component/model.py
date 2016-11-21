#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
import peewee
deferred_db = peewee.SqliteDatabase(None)

STAUS_WAIT_TAKING = 0 # 待揽件
STAUS_IN_TRANSIT = 1 # 运输中
STAUS_IN_DELIVERING = 2 # 派件中
STAUS_IN_DELIVERED = 3 # 已签收


class BaseModel(peewee.Model):
    class Meta:
        database = deferred_db


class PackageTrackingRecord(BaseModel):
    #qq昵称
    qq_nick_name = peewee.CharField(null=False)
    #qq号
    qq_no = peewee.CharField(null=False)
    #订阅的群
    qq_group_no = peewee.CharField(null=True)
    #订阅的群号
    qq_group_name = peewee.CharField(null=True)
    #快递单号
    tracking_no = peewee.CharField(null=False)
    #快递公司
    tracking_company_name = peewee.CharField(null=True)
    #当前状态 0 待揽收 1 运输中 2 派送中 3 已签收
    package_status = peewee.IntegerField(null=False, default=0)

    #创建时间
    create_time = peewee.DateTimeField(null=False, default=datetime.datetime.now())
    #更新时间
    update_time = peewee.DateTimeField(null=False)


class PackageTrackingDetail(BaseModel):
    package_tracking = peewee.ForeignKeyField(PackageTrackingRecord, related_name='logs')
    traking_no = peewee.CharField(null=True)
    tracking_msg = peewee.CharField(null=True)
    update_time = peewee.DateTimeField(null=False)
    update_time_int = peewee.IntegerField(null=False)