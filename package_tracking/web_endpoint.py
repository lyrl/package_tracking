#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import re
import web
from component.pkg_trk_component import PkgTrkComponentImpl

urls = (
  '/api/qq', 'index'
)

pkg_trk_comp = PkgTrkComponentImpl(create_table=False, mojoqq_host='192.168.1.84')
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

                if re.match('^查询快递 \d+$', content):
                    pkg_trk_comp.qry_pkg_trk_msg(
                        req_json['sender'].encode('utf-8'),
                        str(req_json['sender_qq']),
                        str(req_json['gnumber']),
                        req_json['group'].encode('utf-8'),
                        str(content).replace('查询快递 ', ''),
                        True
                    )
                if re.match('^查询快递详情 \d+$', content):
                    pkg_trk_comp.qry_pkg_trk_msg(
                        req_json['sender'].encode('utf-8'),
                        str(req_json['sender_qq']),
                        str(req_json['gnumber']),
                        req_json['group'].encode('utf-8'),
                        str(content).replace('查询快递详情 ', ''),
                        False
                    )
                if re.match('^订阅快递状态 \d+$', content):
                    pkg_trk_comp.sub_pkg_trk_msg(
                        req_json['sender'].encode('utf-8'),
                        str(req_json['sender_qq']),
                        str(req_json['gnumber']),
                        req_json['group'].encode('utf-8'),
                        str(content).replace('订阅快递状态 ', ''),
                        True
                    )
        else:
            pass

        return "success"


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()