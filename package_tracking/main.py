#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import sys
import os

import time

path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)

from package_tracking.component.package_tracking import PackageTrackingComponentImpl

if __name__ == '__main__':
    while True:
        package_tracking_impl = PackageTrackingComponentImpl(create_table=True, mojoqq_host='127.0.0.1')
        package_tracking_impl.update_subscribed_package()

        time.sleep(60)