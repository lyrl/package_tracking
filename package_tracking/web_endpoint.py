#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import re
import web
import os
import sys

path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)

from package_tracking.component.package_tracking import PackageTrackingComponentImpl

urls = (
  '/api/qq', 'QQ',
  '/api/wx', 'WX',
)

pkg_trk_comp = PackageTrackingComponentImpl(create_table=False, mojoqq_host='127.0.0.1')
# pkg_trk_comp = PackageTrackingComponentImpl(create_table=False, mojoqq_host='192.168.30.130')


class QQ:
    def GET(self):
        return "Hello, world!"

    def POST(self):
        data = web.data()
        req_json = json.loads(data)
        print data

        if req_json['type'] == 'group_message':
            if req_json['content']:
                content = req_json['content'].encode('utf-8')
                content = content.replace(' ', '')

                if re.match('^快递\w+$', content):
                    pkg_trk_comp.qry_pkg_trk_msg(
                        req_json['sender_qq'].encode('utf-8'),
                        req_json['sender'].encode('utf-8'),
                        req_json['group'].encode('utf-8'),
                        req_json['group_id'].encode('utf-8'),
                        'group',
                        'qq',
                        str(content).replace('快递', '')
                    )
                if re.match('^快递跟踪\w+$', content):
                    pkg_trk_comp.sub_pkg_trk_msg(
                        req_json['sender_qq'].encode('utf-8'),
                        req_json['sender'].encode('utf-8'),
                        req_json['group'].encode('utf-8'),
                        req_json['group_id'].encode('utf-8'),
                        'group',
                        'qq',
                        str(content).replace('快递跟踪', ''))
        elif req_json['type'] == 'message':
            if req_json['content']:
                content = req_json['content'].encode('utf-8')
                content = content.replace(' ', '')

                if re.match('^快递\w+$', content):
                    pkg_trk_comp.qry_pkg_trk_msg(
                        req_json['sender_qq'].encode('utf-8'),
                        req_json['sender'].encode('utf-8'),
                        None,
                        None,
                        'group',
                        'qq',
                        str(content).replace('快递', ''))
                if re.match('^快递跟踪\w+$', content):
                    pkg_trk_comp.sub_pkg_trk_msg(
                        req_json['sender_qq'].encode('utf-8'),
                        req_json['sender'].encode('utf-8'),
                        None,
                        None,
                        'group',
                        'qq',
                        str(content).replace('快递跟踪', ''))

        return "success"

class WX:
    def GET(self):
        return "Hello, world!"

    def POST(self):
        data = web.data()
        req_json = json.loads(data)
        print data

        if req_json['type'] == 'group_message':
            if req_json['content']:
                content = req_json['content'].encode('utf-8')
                content = content.replace(' ', '')

                if re.match('^快递\w+$', content):
                    pkg_trk_comp.qry_pkg_trk_msg(
                        None,
                        req_json['sender'].encode('utf-8'),
                        req_json['group_id'].encode('utf-8'),
                        None,
                        'group',
                        'wx',
                        str(content).replace('快递', ''))
                if re.match('^快递跟踪\w+$', content):
                    pkg_trk_comp.sub_pkg_trk_msg(
                        None,
                        req_json['sender'].encode('utf-8'),
                        req_json['group_id'].encode('utf-8'),
                        None,
                        'group',
                        'wx',
                        str(content).replace('快递跟踪', ''))
        elif req_json['type'] == 'friend_message':
            if req_json['content']:
                content = req_json['content'].encode('utf-8')
                content = content.replace(' ', '')

                if re.match('^快递\w+$', content):
                    pkg_trk_comp.qry_pkg_trk_msg(
                        req_json['sender_account'].encode('utf-8'),
                        req_json['sender'].encode('utf-8'),
                        req_json['group_id'].encode('utf-8'),
                        None,
                        'friend',
                        'wx',
                        str(content).replace('快递', ''))
                if re.match('^快递跟踪\w+$', content):
                    pkg_trk_comp.sub_pkg_trk_msg(
                        req_json['sender_account'].encode('utf-8'),
                        req_json['sender'].encode('utf-8'),
                        req_json['group_id'].encode('utf-8'),
                        None,
                        'friend',
                        'wx',
                        str(content).replace('快递跟踪', ''))

        return "success"


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()