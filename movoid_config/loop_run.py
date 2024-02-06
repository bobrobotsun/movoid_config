#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : loop_run
# Author        : Sun YiFan-Movoid
# Time          : 2024/2/6 20:17
# Description   : 
"""
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
                self.start_main()
            except Exception as err:
                print(f'something wrong happened:{err}')
            finally:
                try:
                    input_str = input('process ended.you can input nothing to exit,or input anything to rerun it:')
                except:  # noqa
                    break
                else:
                    if input_str:
                        continue
                    else:
                        break

    def start_main(self):
        pass


if __name__ == '__main__':
    pass
