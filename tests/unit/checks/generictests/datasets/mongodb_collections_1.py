# yapf: disable


checkname = 'mongodb_collections'


info = [
        [u'admin', u'system.version', u'avgObjSize', u'59'],
        [u'admin', u'system.version', u'totalIndexSize', u'16384'],
        [u'admin', u'system.version', u'storageSize', u'16384'],
        [u'admin', u'system.version', u'indexSizes', u"{u'_id_': 16384}"],
        [u'admin', u'system.version', u'size', u'59'],
        [u'local', u'startup_log', u'avgObjSize', u'1948'],
        [u'local', u'startup_log', u'indexSizes', u"{u'_id_': 36864}"],
        [u'local', u'startup_log', u'totalIndexSize', u'36864'],
        [u'local', u'startup_log', u'maxSize', u'10485760'],
        [u'local', u'startup_log', u'storageSize', u'36864'],
        [u'local', u'startup_log', u'size', u'5844'],
        [u'test', u'zips', u'avgObjSize', u'94'],
        [u'test', u'zips', u'totalIndexSize', u'315392'],
        [u'test', u'zips', u'storageSize', u'1462272'],
        [u'test', u'zips', u'indexSizes', u"{u'_id_': 315392}"],
        [u'test', u'zips', u'size', u'2774134'],
        [u'config', u'system.sessions', u'ns', u'config.system.sessions'],
        [u'config', u'system.sessions', u'ok', u'1.0'],
        [u'config', u'system.sessions', u'avgObjSize', u'99'],
        [u'config', u'system.sessions', u'totalIndexSize', u'49152'],
        [u'config', u'system.sessions', u'storageSize', u'24576'],
        [u'config',
         u'system.sessions',
         u'indexSizes',
         u"{u'_id_': 24576, u'lsidTTLIndex': 24576}"],
        [u'config', u'system.sessions', u'size', u'594']]


discovery = {'': [(u'admin system.version', {}),
                  (u'config system.sessions', {}),
                  (u'local startup_log', {}),
                  (u'test zips', {})]}


checks = {'': [(u'admin system.version',
                {'inodes_levels': (10.0, 5.0),
                 'levels': (80.0, 90.0),
                 'levels_low': (50.0, 60.0),
                 'magic_normsize': 20,
                 'show_inodes': 'onlow',
                 'show_levels': 'onmagic',
                 'show_reserved': False,
                 'trend_perfdata': True,
                 'trend_range': 24},
                [(0,
                  '0.36% used (59.00 B of 16.00 kB), trend: 0.00 B / 24 hours',
                  [(u'admin_system.version',
                    5.626678466796875e-05,
                    0.0125,
                    0.0140625,
                    0,
                    0.015625),
                   ('fs_size', 0.015625, None, None, None, None),
                   ('growth', 0.0, None, None, None, None),
                   ('trend', 0, None, None, 0, 0.0006510416666666666)])]),
               (u'config system.sessions',
                {'inodes_levels': (10.0, 5.0),
                 'levels': (80.0, 90.0),
                 'levels_low': (50.0, 60.0),
                 'magic_normsize': 20,
                 'show_inodes': 'onlow',
                 'show_levels': 'onmagic',
                 'show_reserved': False,
                 'trend_perfdata': True,
                 'trend_range': 24},
                [(0,
                  '2.42% used (594.00 B of 24.00 kB), trend: 0.00 B / 24 hours',
                  [(u'config_system.sessions',
                    0.0005664825439453125,
                    0.01875,
                    0.02109375,
                    0,
                    0.0234375),
                   ('fs_size', 0.0234375, None, None, None, None),
                   ('growth', 0.0, None, None, None, None),
                   ('trend', 0, None, None, 0, 0.0009765625)])]),
               (u'local startup_log',
                {'inodes_levels': (10.0, 5.0),
                 'levels': (80.0, 90.0),
                 'levels_low': (50.0, 60.0),
                 'magic_normsize': 20,
                 'show_inodes': 'onlow',
                 'show_levels': 'onmagic',
                 'show_reserved': False,
                 'trend_perfdata': True,
                 'trend_range': 24},
                [(0,
                  '15.9% used (5.71 of 36.00 kB), trend: 0.00 B / 24 hours',
                  [(u'local_startup_log',
                    0.005573272705078125,
                    0.028125,
                    0.031640625,
                    0,
                    0.03515625),
                   ('fs_size', 0.03515625, None, None, None, None),
                   ('growth', 0.0, None, None, None, None),
                   ('trend', 0, None, None, 0, 0.00146484375)])]),
               (u'test zips',
                {'inodes_levels': (10.0, 5.0),
                 'levels': (80.0, 90.0),
                 'levels_low': (50.0, 60.0),
                 'magic_normsize': 20,
                 'show_inodes': 'onlow',
                 'show_levels': 'onmagic',
                 'show_reserved': False,
                 'trend_perfdata': True,
                 'trend_range': 24},
                [(2,
                  '189.7% used (2.65 of 1.39 MB), (warn/crit at 80.0%/90.0%), trend: 0.00 B / 24 hours',
                  [(u'test_zips',
                    2.645620346069336,
                    1.115625,
                    1.255078125,
                    0,
                    1.39453125),
                   ('fs_size', 1.39453125, None, None, None, None),
                   ('growth', 0.0, None, None, None, None),
                   ('trend', 0, None, None, 0, 0.05810546875)])])]}
