#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
from abc import ABCMeta, abstractmethod
from multiprocessing import Process

from peewee import SQL

import model
import util
from kuaidi100 import Kuaidi100ComponentImpl
from mojo_qq import MoJoQQComponentImpl
from mojo_wx import MoJoWXComponentImpl
from package_tracking_repo import PackageTrackingRepoComponentImpl

logger = util.get_logger("PackageTracking")


class PackageTrackingComponent:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def sub_pkg_trk_msg(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no):
        pass

    @abstractmethod
    def qry_pkg_trk_msg(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no, brief=True):
        pass


class PackageTrackingComponentImpl(PackageTrackingComponent):
    def __init__(self, db_path='./sqlite3.db', create_table=False, mojoqq_host='127.0.0.1', mojoqq_port='5000', mojowx_host='127.0.0.1', mojowx_port='3000'):
        """
        包裹订阅查询实现

        Args:
            db_path (str): sqlite3数据库文件路径 eg: /root/sqlite3.db
            create_table (bool): 是否需要自动创建表
            mojoqq_host (str): mojoqq ip
            mojoqq_port (str): mojoqq 端口
            mojowx_host (str): mojowx ip
            mojowx_port (str): mojowx 端口
        """
        self.mojo_wx = MoJoWXComponentImpl(mojowx_host, mojowx_port)
        self.mojo_qq = MoJoQQComponentImpl(mojoqq_host, mojoqq_port)
        self.pkg_trk_repo = PackageTrackingRepoComponentImpl(db_path, create_table)
        self.kuaidi100 = Kuaidi100ComponentImpl()

    def sub_pkg_trk_msg(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no):
        """
        订阅包裹更新状态

        Args:
            suber_account (str): 订阅者账号
            suber_nike_name (str): 订阅者昵称
            group_name (str): 群组名
            group_no (str): 群组号
            sub_type (str): 私人信息，群组信息
            sub_source (str): 订阅来源 qq wx
            tracking_no (str): 快递单号
        # Returns:
        #     model.PackageTrackingRecord: 跟踪记录
        """
        # 查询用户是否重复订阅
        # result = self.pkg_trk_repo.query(qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no)
        #
        # print result
        #
        # for i in result:
        #     print i.id
        #
        # if result and result.count() > 0:
        #     msg = '您已经订阅了此快递动态，请勿重复订阅！'
        #
        #     for i in result:
        #         if i.package_status == model.STAUS_IN_DELIVERED:
        #             msg = '当前快递是已签收状态，无法提供订阅服务！'
        #
        #     self.send_async_group_msg(qq_group_no, msg, qq_nike_name)
        #     return

        pkg_trk_record = self.pkg_trk_repo.new_pkg_trk_rec(suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no)

        kuai100_resp = self.kuaidi100.query_trk_detail(tracking_no)

        msg = ''

        if PkgTrkUtil.check_kuai100_resp(kuai100_resp):
            trk_logs = kuai100_resp['data']['info']['context']

            # 存储快递跟踪信息到数据库
            for log in trk_logs:
                time = datetime.datetime.fromtimestamp(float(log['time']))
                desc = log['desc'].encode('utf-8')
                self.pkg_trk_repo.new_trk_log(pkg_trk_record, tracking_no, time, desc, int(log['time']))

            # 提取快递公司名称
            com = PkgTrkUtil.extract_company_name(kuai100_resp)

            # 快递公司 快递单号
            #
            # 快递已经到达xxxxxx
            #
            # xxxxxxxxxxxxxxxxx
            #
            # xzxcdasdqweqweqweq

            if com:
                com = com.encode('utf-8')
                msg = '\n' + com + ' ' + str(tracking_no) + '\n'

            msg += '\n\n'.join(PkgTrkUtil.extract_trk_rec(trk_logs, 2))

            # 解析快递状态
            pkg_trk_record.package_status = PkgTrkUtil.parse_tracking_status(trk_logs)

            print 'pkg_trk_record.package_status: ',  str(pkg_trk_record.package_status)

            if pkg_trk_record.package_status == model.STAUS_IN_DELIVERED:
                msg = '当前快递是已签收状态，无法提供订阅服务！'
            else:
                msg = '快递已订阅，将为您提供实时推送！'

            # 更新快递公司名
            if kuai100_resp['data'].has_key('company'):
                pkg_trk_record.company_name = kuai100_resp['data']['company']['fullname']

            pkg_trk_record.save()
        else:
            msg = '该单号暂无物流进展，有进展时会通过QQ群消息提醒!'

        # self.send_async_group_msg(qq_group_no, msg, qq_nike_name)

    def qry_pkg_trk_msg(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no, brief=True):
        """
        查询快递最新状态

        Args:
            suber_account (str): 订阅者账号
            suber_nike_name (str): 订阅者昵称
            group_name (str): 群组名
            group_no (str): 群组号
            sub_type (str): 私人信息，群组信息
            sub_source (str): 订阅来源 qq wx
            tracking_no (str): 快递单号
            brief (bool): 是否只发送前3条信息
        # Returns:
        #     model.PackageTrackingRecord: 跟踪记录
        """

        kuai100_resp = self.kuaidi100.query_trk_detail(tracking_no)

        msg = ''

        if PkgTrkUtil.check_kuai100_resp(kuai100_resp):
            trk_logs = kuai100_resp['data']['info']['context']

            # 提取快递公司名称
            com = PkgTrkUtil.extract_company_name(kuai100_resp)

            # 快递公司 快递单号
            #
            # 快递已经到达xxxxxx
            #
            # xxxxxxxxxxxxxxxxx
            #
            # xzxcdasdqweqweqweq

            if com:
                com = com.encode('utf-8')
                msg = '\n' + com + ' ' + str(tracking_no) + '\n'

            if brief:
                msg += '\n\n'.join(PkgTrkUtil.extract_trk_rec(trk_logs, 3))
            else:
                msg += '\n\n'.join(PkgTrkUtil.extract_trk_rec(trk_logs, 100))

        else:
            msg = tracking_no + ' ' + kuai100_resp['msg'].encode('utf-8')


        # if sub_source == 'qq':
        #     self.send_async_group_msg(str(qq_group_no), msg, qq_nike_name)
        # else:
        #     self.send_async_group_msg(str(qq_group_no), msg, qq_nike_name)


        PkgTrkUtil.send_msg(suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no, brief, msg)

    def update_subscribed_package(self):
        """
        更新数据库中订阅的快递
        """
        logger.debug("[包裹追踪] - 准备更新包裹!")

        all_in_transiting_pkgs = self.pkg_trk_repo.list_all_in_transiting_pkg()

        for pkg in all_in_transiting_pkgs:
            logger.debug("[包裹追踪] - 开始更新 %s !" % str(pkg.tracking_no))
            kuaidi100_resp = self.kuaidi100.query_trk_detail(pkg.tracking_no)

            if PkgTrkUtil.check_kuai100_resp(kuaidi100_resp):
                pkg.tracking_company_name = PkgTrkUtil.extract_company_name(kuaidi100_resp)
                pkg.save()

                trk_logs = kuaidi100_resp['data']['info']['context']

                top_time = 0

                trk_log_entiry = pkg.logs.order_by(SQL('update_time').desc())

                for i in trk_log_entiry:
                    tmp = int(i.update_time_int)
                    if tmp > top_time:
                        top_time = tmp

                logger.debug('top_time' + str(top_time))

                for i in trk_logs:
                    if int(i['time']) > top_time:
                        time = datetime.datetime.fromtimestamp(float(i['time']))
                        desc = i['desc'].encode('utf-8')
                        self.pkg_trk_repo.new_trk_log(pkg, pkg.tracking_no, time, desc, int(i['time']))
                        pkg.package_status = PkgTrkUtil.parse_tracking_status(trk_logs)
                        pkg.update_time = datetime.datetime.now()
                        pkg.save()
                        logger.debug("[包裹追踪] - 最新更新信息 %s  %s !" % (str(pkg.tracking_no), desc))

                        msg = '\n\n %s %s 快递状态更新!\n\n %s %s' % (
                            pkg.tracking_company_name.encode('utf-8'),
                            pkg.tracking_no.encode('utf-8'),
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            desc
                        )

                        self.send_async_group_msg(pkg.qq_group_no.encode('utf-8'), msg, pkg.qq_nick_name.encode('utf-8'))
                        break
            else:
                logger.debug("[包裹追踪] - 包裹 %s 没有任何更新!" % str(pkg.tracking_no))

        logger.debug("[包裹追踪] - 全部遍历完成等待60秒后再次遍历!")

    def send_async_group_msg(self, qq_group_no, msg, qq_nike_name):
        """
        mojoqq信息采用异步方式发送
        """
        Process(target=self.mojo_qq.send_group_msg, args=(qq_group_no, msg, qq_nike_name,)).start()

    def send_msg(self, suber_account, suber_nike_name, group_name, group_no, sub_type, sub_source, tracking_no, brief,
                 msg):
        """
        查询快递最新状态

        Args:
            suber_account (str): 订阅者账号
            suber_nike_name (str): 订阅者昵称
            group_name (str): 群组名
            group_no (str): 群组号
            sub_type (str): 私人信息，群组信息
            sub_source (str): 订阅来源 qq wx
            tracking_no (str): 快递单号
            brief (bool): 是否只发送前3条信息
            msg (str): 消息
        pass
        """

        if sub_source == 'qq':
            if sub_type == 'friend':
                self.mojo_qq.send_qq_msg(suber_account, msg)
            elif sub_type == 'group':
                self.mojo_qq.send_group_msg(group_no, msg, suber_nike_name)
        elif sub_source == 'wx':
            if sub_type == 'friend':
                self.mojo_wx.send_msg(suber_account, msg)
            elif sub_type == 'group':
                self.mojo_wx.send_group_msg(group_name, msg, suber_nike_name)


class PkgTrkUtil:

    def __init__(self):
        pass

    @staticmethod
    def extract_trk_rec(trk_logs, count=3):
        """
        获取快递记录前3条
        Args:
            trk_logs (list of dict): 快递更新状态

            示例数据:
            [
                {
                  "time": "1479458247",
                  "desc": "派件已签收，签收人是PDA图片签收,签收网点是北京昌平回龙观公司,"
                },
                {
                  "time": "1479427252",
                  "desc": "北京昌平回龙观公司,的王士全,正在派件,扫描员回龙观观主,"
                },
                {
                  "time": "1479423900",
                  "desc": "快件到达北京昌平回龙观公司,上一站是北京分拨中心,扫描员华电大学,"
                }
            ]

            count (int): 快递状态的前几条 默认 3

        Returns:
            list of str: 重新格式化的快递动态信息

            示例：
                [
                  "2016-11-18 00:37:27 派件已签收，签收人是PDA图片签收,签收网点是北京昌平回龙观公司,"
                  "2016-11-17 16:00:52 北京昌平回龙观公司,的王士全,正在派件,扫描员回龙观观主,"
                  "2016-11-17 15:05:00 快件到达北京昌平回龙观公司,上一站是北京分拨中心,扫描员华电大学,"
                ]
        """
        msg = []

        for i in trk_logs[:count]:
            time = datetime.datetime.fromtimestamp(float(i['time']))
            msg.append(time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + i['desc'].encode('utf-8'))
        return msg

    @staticmethod
    def parse_tracking_status(trk_logs):
        """
        根据快递更新记录解析快递当前的状态

        Args:
            trk_logs (list of dict): 快递更新状态

            示例数据:
            [
                {
                  "time": "1479458247",
                  "desc": "派件已签收，签收人是PDA图片签收,签收网点是北京昌平回龙观公司,"
                },
                {
                  "time": "1479427252",
                  "desc": "北京昌平回龙观公司,的王士全,正在派件,扫描员回龙观观主,"
                },
                {
                  "time": "1479423900",
                  "desc": "快件到达北京昌平回龙观公司,上一站是北京分拨中心,扫描员华电大学,"
                }
            ]


        Returns:
            int: 快递状态


            STAUS_WAIT_TAKING = 0 # 待揽件
            STAUS_IN_TRANSIT = 1 # 运输中
            STAUS_IN_DELIVERING = 2 # 派件中
            STAUS_IN_DELIVERED = 3 # 已签收

        """

        if trk_logs:
            for log in trk_logs:
                desc = log['desc'].encode('utf-8')

                if desc.find('已签收')>0 or desc.find('投递并签收')>0:
                    print desc
                    return model.STAUS_IN_DELIVERED

                if desc.find('派件中')>0 or desc.find('正在派件')>0 :
                    return model.STAUS_IN_DELIVERING

        return model.STAUS_IN_TRANSIT

    @classmethod
    def extract_company_name(cls, kuai100_resp):
        """
        从快递查询接口的返回信息中获取快递公司名称

        Args:
            kuai100_resp (dict): 快递100接口返回json数据对象

            示例数据:
            {
              "msg": "",
              "status": "0",
              "error_code": "0",
              "data": {
                "info": {
                  "status": "1",
                  "com": "kuaijiesudi",
                  "state": "3",
                  "context": [
                    {
                      "time": "1479458247",
                      "desc": "派件已签收，签收人是PDA图片签收,签收网点是北京昌平回龙观公司,"
                    }
                  ],
                  "_source_com": ""
                },
                "com": "kuaijiesudi",
                "company": {
                  "url": "http://www.kuaidi100.com/all/kjkd.shtml?from=openv",
                  "fullname": "快捷快递",
                  "shortname": "快捷"
                }
              }
            }


        Returns:
           str: 快递公司名称
        """

        if kuai100_resp['data'].has_key('company'):
            return kuai100_resp['data']['company']['fullname']

        return None

    @classmethod
    def check_kuai100_resp(cls, kuai100_resp):
        """
        检查快递100返回报文，看查询是否成功


        Args:
            kuai100_resp (dict): 快递100接口返回json数据对象

            示例数据:
            {
              "msg": "",
              "status": "0",
              "error_code": "0",
              "data": {
                "info": {
                  "status": "1",
                  "com": "kuaijiesudi",
                  "state": "3",
                  "context": [
                    {
                      "time": "1479458247",
                      "desc": "派件已签收，签收人是PDA图片签收,签收网点是北京昌平回龙观公司,"
                    }
                  ],
                  "_source_com": ""
                },
                "com": "kuaijiesudi",
                "company": {
                  "url": "http://www.kuaidi100.com/all/kjkd.shtml?from=openv",
                  "fullname": "快捷快递",
                  "shortname": "快捷"
                }
              }
            }
        Returns:
           bool: 查询是否成功
        """

        if not kuai100_resp:
            return False

        if int(kuai100_resp['status']) != 0 or int(kuai100_resp['error_code']) != 0:
            return False

        if kuai100_resp.has_key('data') and kuai100_resp['data'] :
            if kuai100_resp['data'].has_key('info') and kuai100_resp['data']['info']:
                if kuai100_resp['data']['info'].has_key('context') and kuai100_resp['data']['info']['context']:
                    return True
        return False

class PackageTrackingComponentException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message



