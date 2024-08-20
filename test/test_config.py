#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_config
# Author        : Sun YiFan-Movoid
# Time          : 2024/8/20 22:26
# Description   : 
"""
from pathlib import Path
from movoid_config import Config


class TestConfig:
    def test_config_not_write(self):
        config = Config({
            'test': {
                'default': 'test_str'
            }
        }
            , _file='config_not_write.ini'
            , _file_write=False)
        assert config.test == 'test_str'
        assert not Path('config_not_write.ini').exists()

    def test_config_not_write2(self):
        config = Config({
            'test': {
                'default': 'test_str'
            }
        }
            , _file='test/config_not_write2.ini'
            , _file_write=False
        )
        assert config.test == 'in_ini'
        assert Path('test/config_not_write2.ini').exists()
