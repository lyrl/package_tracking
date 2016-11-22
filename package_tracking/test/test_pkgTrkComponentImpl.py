from unittest import TestCase
from package_tracking.component.package_tracking import PkgTrkComponentImpl


class TestPkgTrkComponentImpl(TestCase):
    def test_sub_pkg_trk_msg(self):
        pkg_trk = PkgTrkComponentImpl(mojoqq_host='192.168.30.130', create_table=False)
        # pkg_trk.sub_pkg_trk_msg('lyrl', '184387904', '498880156', 'Mojo-Webqq', '418485853713', True)
        # pkg_trk.qry_pkg_trk_msg('lyrl', '184387904', '498880156', 'Mojo-Webqq', '4184858537133', True)
