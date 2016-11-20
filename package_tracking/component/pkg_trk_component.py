#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
from abc import ABCMeta, abstractmethod

from peewee import SQL

import model
import util
from kuaidi100_compoent import Kuaidi100ComponentImpl
from mojo_qq_compoent import MoJoQQComponentImpl
from pkg_trk_repo_component import PkgTrkRepoComponentImpl

logger = util.get_logger("PackageTracking")


class PkgTrkComponent:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def sub_pkg_trk_msg(self, qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no, top3):
        pass

    @abstractmethod
    def qry_pkg_trk_msg(self, qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no, top3):
        pass


class PkgTrkComponentImpl(PkgTrkComponent):
    def __init__(self, db_path='./sqlite3.db', create_table=False, mojoqq_host='127.0.0.1', mojoqq_port='5000'):
        """
        包裹订阅查询实现

        Args:
            db_path (str): sqlite3数据库文件路径 eg: /root/sqlite3.db
            create_table (bool): 是否需要自动创建表
            mojoqq_host (str): mojoqq ip
            mojoqq_port (str): mojoqq 端口
        """

        self.mojo_qq = MoJoQQComponentImpl(mojoqq_host, mojoqq_port)
        self.pkg_trk_repo = PkgTrkRepoComponentImpl(db_path, create_table)
        self.kuaidi100 = Kuaidi100ComponentImpl()

    def sub_pkg_trk_msg(self, qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no, top3=True):
        """
        订阅包裹更新状态

        Args:
            qq_nike_name (str): 订阅者qq昵称
            qq_no (str): 订阅者qq号
            qq_group_no (str): 订阅者所在群号
            qq_group_name (str): 订阅者所在群名
            tracking_no (str): 快递单号、包裹单号
            top3 (bool): 是否只取最新的三条动态
        # Returns:
        #     model.PackageTrackingRecord: 跟踪记录
        """

        pkg_trk_record = self.pkg_trk_repo.new_pkg_trk_rec(qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no)

        kuai100_resp = self.kuaidi100.query_trk_detail(tracking_no)

        msg = ''

        if kuai100_resp.has_key('data') and kuai100_resp['data'].has_key('info') and kuai100_resp['data']['info'].has_key('context'):
            trk_logs = kuai100_resp['data']['info']['context']

            # 存储快递跟踪信息到数据库
            for log in trk_logs:
                time = datetime.datetime.fromtimestamp(float(log['time']))
                desc = log['desc'].encode('utf-8')
                self.pkg_trk_repo.new_trk_log(pkg_trk_record, tracking_no, time, desc)

            # 提取快递公司名称
            com = PkgTrkUtil.extract_com(kuai100_resp)

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

            if pkg_trk_record.package_status != model.STAUS_IN_DELIVERED:
                msg = '当前快递是已签收状态，无法提供订阅服务！'
            else:
                msg = '快递已订阅，将为您提供实时推送！'

            # 更新快递公司名
            if kuai100_resp['data'].has_key('company'):
                pkg_trk_record.tracking_company_name = kuai100_resp['data']['company']['fullname']

            pkg_trk_record.save()
        else:
            msg = '该单号暂无物流进展，有进展时会通过QQ群消息提醒!'

        self.mojo_qq.send_group_msg(qq_group_no, msg, qq_nike_name)

    def qry_pkg_trk_msg(self, qq_nike_name, qq_no, qq_group_no, qq_group_name, tracking_no, top3):
        """
        查询快递最新状态

        Args:
            qq_nike_name (str): 订阅者qq昵称
            qq_no (str): 订阅者qq号
            qq_group_no (str): 订阅者所在群号
            qq_group_name (str): 订阅者所在群名
            tracking_no (str): 快递单号、包裹单号
            top3 (bool): 是否只取最新的三条动态
        # Returns:
        #     model.PackageTrackingRecord: 跟踪记录
        """

        kuai100_resp = self.kuaidi100.query_trk_detail(tracking_no)

        msg = ''

        if PkgTrkUtil.isSuccess(kuai100_resp):
        # if kuai100_resp.has_key('data') and kuai100_resp['data'].has_key('info') and kuai100_resp['data']['info'].has_key('context'):
            trk_logs = kuai100_resp['data']['info']['context']

            # 提取快递公司名称
            com = PkgTrkUtil.extract_com(kuai100_resp)

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

            if top3:
                msg += '\n\n'.join(PkgTrkUtil.extract_trk_rec(trk_logs, 3))
            else:
                msg += '\n\n'.join(PkgTrkUtil.extract_trk_rec(trk_logs, 100))

        else:
            msg = '该单号暂无物流进展！'

        self.mojo_qq.send_group_msg(str(qq_group_no), msg, qq_nike_name)

    def update_subscribed_package(self):
        """
        更新数据库中订阅的快递
        """
        logger.debug("[包裹追踪] - 准备更新包裹!")

        all_in_transiting_pkgs = self.pkg_trk_repo.list_all_in_transiting_pkg()

        for pkg in all_in_transiting_pkgs:
            logger.debug("[包裹追踪] - 开始更新 %s !" % str(pkg.tracking_no))
            traking_json = self.kuaidi100.query_trk_detail(pkg.tracking_no)

            # 先更新快递公司名称
            if traking_json['data'].has_key('company'):
                pkg.tracking_company_name = traking_json['data']['company']['fullname']
                pkg.update_time = datetime.datetime.now()
                pkg.save()

            if PkgTrkUtil.isSuccess(traking_json):
                trk_info = traking_json['data']['info']['context']

                time_stemp = trk_info[0]['time']
                logger.debug('time_stemp' + str(time_stemp))
                top_time = 0

                trk_log_entiry = pkg.logs.order_by(SQL('update_time').desc())

                for i in trk_log_entiry:
                    print i.id
                    tmp = (i.update_time - datetime.datetime(1970, 1, 1)).total_seconds()
                    off = (datetime.datetime.utcnow() - datetime.datetime.now()).total_seconds()

                    print 'tmp' + str(int(tmp+off))
                    if tmp > top_time:
                        top_time = int(tmp+off)

                logger.debug('top_time' + str(top_time))

                for i in trk_info:
                    if int(i['time']) > top_time:
                        time = datetime.datetime.fromtimestamp(float(i['time']))
                        desc = i['desc'].encode('utf-8')
                        self.pkg_trk_repo.new_trk_log(pkg, pkg.tracking_no, time, desc)
                        pkg.package_status = PkgTrkUtil.parse_tracking_status(trk_info)
                        pkg.update_time = datetime.datetime.now()
                        pkg.save()
                        logger.debug("[包裹追踪] - 最新更新信息 %s  %s !" % (str(pkg.tracking_no), desc))

                        msg = '\n %s %s 快递状态更新!\n %s %s' % (
                            pkg.tracking_company_name.encode('utf-8'),
                            pkg.tracking_no.encode('utf-8'),
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            desc
                        )

                        self.mojo_qq.send_group_msg(pkg.qq_group_no.encode('utf-8'), msg, pkg.qq_nick_name.encode('utf-8'))
                        break
            else:
                logger.debug("[包裹追踪] - 包裹 %s 没有任何更新!" % str(pkg.tracking_no))

        logger.debug("[包裹追踪] - 全部遍历完成等待60秒后再次遍历!")


class PkgTrkUtil:

    def __init__(self):
        pass

    @staticmethod
    def extract_trk_rec(trk_logs, count=3):
        """
        获取快递记录前3条
        """
        msg = []

        for i in trk_logs[:count]:
            time = datetime.datetime.fromtimestamp(float(i['time']))
            msg.append(time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + i['desc'].encode('utf-8'))
        return msg

    @staticmethod
    def parse_tracking_status(trk_logs):
        if trk_logs:
            for log in trk_logs:
                desc = log['desc'].encode('utf-8')
                if desc.find('已签收'):
                    return model.STAUS_IN_DELIVERED
                if desc.find('派件中') or desc.find('正在派件') or desc.find('派送中'):
                    return model.STAUS_IN_DELIVERING

        return model.STAUS_IN_TRANSIT

    @classmethod
    def extract_com(cls, kuai100_resp):
        if kuai100_resp['data'].has_key('company'):
            return kuai100_resp['data']['company']['fullname']

        return None

    @classmethod
    def isSuccess(cls, kuai100_resp):
        if kuai100_resp.has_key('data') and kuai100_resp['data'].has_key('info'):
            if kuai100_resp['data']['info']:
                if kuai100_resp['data']['info'].has_key('context'):
                    return True
        return False

class PkgTrkException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message



