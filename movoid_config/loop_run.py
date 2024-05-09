#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : loop_run
# Author        : Sun YiFan-Movoid
# Time          : 2024/2/6 20:17
# Description   : 
"""
import traceback

from .config import Config


class CmdLoopRun:
    def __init__(self, start_now=True, **kwargs):
        self._config = Config()
        if start_now:
            self.start()

    def init_config(self):
        pass

    def start(self):
        while True:
            try:
                print('process started')
                self.init_config()
                self._config.init()
                self.start_main()
            except Exception as err:
                print(f'something wrong happened:{err}')
                traceback.print_exc()
                self.start_exception()
            finally:
                self.start_end()
                try:
                    input_str = input('process ended.you can input nothing to exit,or input anything to rerun it:')
                except:  # noqa
                    self.start_exit()
                    break
                else:
                    if input_str:
                        continue
                    else:
                        self.start_exit()
                        break

    def start_main(self):
        pass

    def start_exception(self):
        pass

    def start_end(self):
        pass

    def start_exit(self):
        pass
