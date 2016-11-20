#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import sys
import os

import time

path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)

from package_tracking.component.pkg_trk_component import PkgTrkComponentImpl

if __name__ == '__main__':
    while True:
        package_tracking_impl = PkgTrkComponentImpl(mojoqq_host='192.168.1.84')
        package_tracking_impl.update_subscribed_package()

        time.sleep(60)