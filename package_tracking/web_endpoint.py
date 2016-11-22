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

from package_tracking.component.package_tracking import PkgTrkComponentImpl

urls = (
  '/api/qq', 'index'
)

pkg_trk_comp = PkgTrkComponentImpl(create_table=False, mojoqq_host='127.0.0.1')
# pkg_trk_comp = PkgTrkComponentImpl(create_table=False, mojoqq_host='192.168.30.130')


class index:
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
                        req_json['sender'].encode('utf-8'),
                        str(req_json['sender_qq']),
                        str(req_json['gnumber']),
                        req_json['group'].encode('utf-8'),
                        str(content).replace('快递', ''),
                        True
                    )
                if re.match('^快递详情\w+$', content):
                    pkg_trk_comp.qry_pkg_trk_msg(
                        req_json['sender'].encode('utf-8'),
                        str(req_json['sender_qq']),
                        str(req_json['gnumber']),
                        req_json['group'].encode('utf-8'),
                        str(content).replace('快递详情', ''),
                        False
                    )
                if re.match('^快递跟踪\w+$', content):
                    pkg_trk_comp.sub_pkg_trk_msg(
                        req_json['sender'].encode('utf-8'),
                        str(req_json['sender_qq']),
                        str(req_json['gnumber']),
                        req_json['group'].encode('utf-8'),
                        str(content).replace('快递跟踪', ''),
                        True
                    )
        else:
            pass

        return "success"


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()