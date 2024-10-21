#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : config
# Author        : Sun YiFan-movoid
# Time          : 2024/1/1 12:27
# Description   : 
"""
import json
import pathlib
import sys
import traceback
from configparser import ConfigParser
from pathlib import Path
from tkinter import Tk, filedialog
from typing import Dict, Union


class Config:
    _analyse: bool = False
    _origin_param = {}
    _origin_list: list = []

    def __init__(self, _dict: Union[Dict[str, dict], None] = None, _file=None, _file_write=True):
        """
        可以直接设置参数类型
        :param _dict:
            key:参数名称，可以以属性形式调用，或者键值的方式调用
            value:
                type:类型，默认str，可以输入
                default：默认值
                single：命令行中单杠单字母，例如输入 -t xx 来决定输入参数
                full：命令行中双杠单词，例如输入 -test xxx 来决定输入参数
                key：命令行中以key-value的模式输入，例如输入 test=value 来决定输入参数
                ini：在配置文件中的路径，一般输入两个字符串，例如输入 main test 来决定在ini文件中的路径输入
                config：是否要从config读取，是否要写入config文件，默认True
                must：该参数是否必须有值。如果没有值会报错。默认True
                ask：如果must的情况下，是否会在无值时向用户询问，仅命令行时生效
                help：在帮助文档中的显示文本。
                false：如果类型是True时，可以在这里输入参数类型，在命令行中输入了这些命令后，会把该值设置为False
                true：如果类型是False时，可以在这里输入参数类型，在命令行中输入了这些命令后，会把该值设置为True
                sub：子类型，针对enum、kv等类型，用于确定这些类型下的取值范围
        :param _file:文件目录，如果不写就不会尝试读写配置文件
        :param _file_write:是否自动写入文件
        """
        Config.init_param()
        self._config_dict = {}
        self.update_rule(_dict)
        self._config_file = _file
        self._config_key = None
        self._config_file_write = bool(_file_write)
        self._value = {}
        self._tk = None
        if _dict is not None:
            self.init(_dict, _file)

    @property
    def file(self):
        return self._config_file

    @file.setter
    def file(self, value):
        self._config_file = value

    def __getitem__(self, item):
        return self._value[item]

    def __setitem__(self, item, value):
        self._value[item] = value

    def __getattr__(self, item):
        return self._value[item]

    def __len__(self):
        return self._value.__len__()

    def items(self):
        return self._value.items()

    def keys(self):
        return self._value.keys()

    def values(self):
        return self._value.values()

    @classmethod
    def init_param(cls):
        if not cls._analyse:
            try:
                cls._origin_param = []
                cls._origin_list = []
                for arg_i, arg_v in enumerate(sys.argv[1:]):
                    if arg_v.startswith('--'):
                        real_argv = arg_v[2:]
                        if real_argv == '':
                            print('please do not input empty config "--",we will ignore it.', file=sys.stderr)
                        else:
                            cls._origin_list.append(['full', real_argv, arg_i])
                    elif arg_v.startswith('-'):
                        real_argv_list = arg_v[1:]
                        if real_argv_list == '':
                            print('please do not input empty config "-",we will ignore it.', file=sys.stderr)
                        else:
                            for real_argv in real_argv_list:
                                cls._origin_list.append(['single', real_argv, arg_i])
                    elif '=' in arg_v:
                        real_arg_key, real_arg_value = arg_v.split('=', 1)
                        if real_arg_key == '':
                            print('please do not input empty config "=*",we will ignore it.', file=sys.stderr)
                        else:
                            cls._origin_list.append(['key', real_arg_key, arg_i, real_arg_value])
                    else:
                        real_argv = arg_v
                        cls._origin_param.append([real_argv, arg_i])
            except Exception as err:
                print(f'we fail to analyse args you input:{err}')
                traceback.print_exc()
                cls._analyse = False
            else:
                cls._analyse = True

    @classmethod
    def get_param(cls, param_index=0, get_count=1):
        param_index = int(param_index)
        get_count = int(get_count)
        index_list = []
        value_list = []
        if get_count <= 0:
            return None
        else:
            for i, v in enumerate(cls._origin_param):
                if v[1] >= param_index:
                    index_list.append(i)
                    value_list.append(v[0])
                    if len(value_list) >= get_count:
                        break
            if len(value_list) < get_count:
                raise Exception(f'param you want {get_count} is more than you left {len(value_list)}')
            for i in index_list[::-1]:
                cls._origin_param.pop(i)
            if get_count == 1:
                return value_list[0]
            else:
                return value_list

    def add_rule(self, name, _type='str', *, _update=True, **kwargs):
        if _update or name not in self._config_dict:
            self._config_dict[name] = {'type': _type, **kwargs}

    def add_multiple_rules(self, _update=True, **kwargs):
        kwargs = dict(kwargs) if kwargs else {}
        for i, v in kwargs.items():
            self.add_rule(i, _update=_update, **v)

    def update_rule(self, rule_dict: Dict[str, dict], _update=True):
        rule_dict = dict(rule_dict) if rule_dict else {}
        for i, v in rule_dict.items():
            self.add_rule(i, _update=_update, **v)

    def init(self, _dict: Dict[str, dict] = None, _file: Union[str, None] = None, _file_write: Union[bool, None] = None):
        self.update_rule(_dict)
        self._config_file = self._config_file if _file is None else _file
        self._config_file_write = self._config_file_write if _file_write is None else bool(_file_write)
        self._value = {}
        self.analyse_config_dict()
        self.read_file()
        self.param_read()
        self.param_default()
        self.param_check()
        if self._config_file_write:
            self.write_file()

    def analyse_config_dict(self):
        self._config_key = {
            'single': {},
            'full': {},
            'key': {},
            'ini': {}
        }
        for key, one_config_dict in self._config_dict.items():
            one_config_dict.setdefault('key', key)
            one_config_dict.setdefault('ini', ['main', key])
            if isinstance(one_config_dict['ini'], str):
                one_config_dict['ini'] = [one_config_dict['ini']]
            if len(one_config_dict['ini']) == 0:
                one_config_dict['ini'].append('main')
            if len(one_config_dict['ini']) == 1:
                one_config_dict['ini'].append(key)
            one_config_dict['ini'] = tuple(one_config_dict['ini'][:2])
            one_config_dict.setdefault('must', False)
            one_config_dict.setdefault('config', True)
            one_config_dict.setdefault('ask', True)
            one_config_dict.setdefault('help', '')
            one_config_dict.setdefault('type', 'str')
            key_type_list = [key, one_config_dict['type']]
            if 'sub' in one_config_dict:
                key_type_list.append(one_config_dict['sub'])
            one_config_dict['type_list'] = key_type_list[1:]
            one_config_dict['type'] = one_config_dict['type'].lower()
            if one_config_dict['type'] in ('f', 'n', 'false', 'no'):
                one_config_dict['type'] = 'false'
                one_config_dict.setdefault('param', 0)
                one_config_dict.setdefault('default', False)
                if 'true' in one_config_dict:
                    if 'single' in one_config_dict['true']:
                        self._config_key['single'][one_config_dict['true']['single']] = [key, 'true']
                    if 'full' in one_config_dict['true']:
                        self._config_key['full'][one_config_dict['true']['full']] = [key, 'true']
                self._config_key['key'][one_config_dict['key']] = [key, 'bool']
                self._config_key['ini'][one_config_dict['ini']] = [key, 'bool']
            elif one_config_dict['type'] in ('t', 'y', 'true', 'yes'):
                one_config_dict['type'] = 'true'
                one_config_dict.setdefault('param', 0)
                one_config_dict.setdefault('default', True)
                if 'false' in one_config_dict:
                    if 'single' in one_config_dict['false']:
                        self._config_key['single'][one_config_dict['false']['single']] = [key, 'false']
                    if 'full' in one_config_dict['false']:
                        self._config_key['full'][one_config_dict['false']['full']] = [key, 'false']
                self._config_key['key'][one_config_dict['key']] = [key, 'bool']
                self._config_key['ini'][one_config_dict['ini']] = [key, 'bool']
            else:
                one_config_dict.setdefault('param', 1)
                self._config_key['key'][one_config_dict['key']] = key_type_list
                self._config_key['ini'][one_config_dict['ini']] = key_type_list
                if one_config_dict['type'] in ('file', 'files', 'dir'):
                    self._tk = Tk()
                    self._tk.withdraw()
            if 'single' in one_config_dict:
                one_config_dict['single'] = str(one_config_dict['single'])[0]
                self._config_key['single'][one_config_dict['single']] = key_type_list
            if 'full' in one_config_dict:
                one_config_dict['full'] = str(one_config_dict['full'])
                self._config_key['full'][one_config_dict['full']] = key_type_list

    @staticmethod
    def change_str_to_target_type(str_value: str, target_type, sub_type=None):
        if target_type == 'int':
            return int(str_value)
        elif target_type == 'float':
            return float(str_value)
        elif target_type == 'number':
            re_value = float(str_value)
            try:
                if float(int(str_value)) == float(str_value):
                    re_value = int(str_value)
            except ValueError:
                re_value = float(str_value)
            finally:
                return re_value
        elif target_type == 'bool':
            return str_value.lower() not in ('f', 'n', 'false', 'no', '')
        elif target_type == 'true':
            return True
        elif target_type == 'false':
            return False
        elif target_type == 'list':
            temp_list = str_value.split(',')
            re_list = []
            for i, v in enumerate(temp_list):
                if v:
                    if sub_type == 'int':
                        re_list.append(int(v))
                    elif sub_type == 'float':
                        re_list.append(float(v))
                    elif sub_type == 'bool':
                        re_list.append(v.lower() not in ('f', 'n', 'false', 'no', ''))
            return re_list
        elif target_type == 'dict':
            temp_list = str_value.split(',')
            re_dict = {}
            for i, v in enumerate(temp_list):
                if ':' in v:
                    temp_key, temp_value = v.split(':')
                    if sub_type[0] == 'int':
                        temp_key = int(temp_key)
                    elif sub_type[0] == 'float':
                        temp_key = float(temp_key)
                    elif sub_type[0] == 'bool':
                        temp_key = temp_key.lower() not in ('f', 'n', 'false', 'no', '')
                    if sub_type[1] == 'int':
                        temp_value = int(temp_value)
                    elif sub_type[1] == 'float':
                        temp_value = float(temp_value)
                    elif sub_type[1] == 'bool':
                        temp_value = temp_value.lower() not in ('f', 'n', 'false', 'no', '')
                    re_dict[temp_key] = temp_value
            return re_dict
        elif target_type == 'enum':
            sub_type_str = [str(_) for _ in sub_type]
            if str_value in sub_type_str:
                return sub_type[sub_type_str.index(str_value)]
            else:
                try:
                    index_value = int(str_value)
                    if index_value <= 0:
                        print('index is less than 1,we use the first option')
                        return sub_type[0]
                    elif index_value > len(sub_type):
                        print(f'index is more than {len(sub_type)},we use the last option')
                        return sub_type[-1]
                    else:
                        print(f'we choose the index of {index_value}')
                        return sub_type[index_value - 1]
                except ValueError:
                    print(f'we do not know what is <{str_value}>, we use the first option')
                    return sub_type[0]
        elif target_type == 'kv':
            return sub_type.get(str_value, str_value)
        elif target_type == 'json':
            return json.loads(str_value)
        elif target_type == 'byte':
            temp_list = str_value.split('.')
            sum_size = 0
            for i in temp_list[:-1]:
                sum_size += int(i)
                sum_size *= 1024
            sum_size += int(temp_list[-1])
            return sum_size
        elif target_type == 'file':
            if str_value == '':
                return str_value
            elif pathlib.Path(str_value).is_file():
                return str(str_value)
            else:
                raise Exception(f'{str_value} is not a file.')
        elif target_type == 'files':
            if str_value == '':
                return []
            else:
                temp_list = str_value.split(',')
                path_list = [pathlib.Path(_).is_file() for _ in temp_list]
                if all(path_list):
                    return temp_list
                else:
                    raise Exception(f'{[_v for _i, _v in enumerate(temp_list) if not path_list[_i]]} is not a file.')
        elif target_type == 'dir':
            if str_value == '':
                return str_value
            elif pathlib.Path(str_value).is_dir():
                return str(str_value)
            else:
                raise Exception(f'{str_value} is not a folder.')
        else:
            return str_value

    @staticmethod
    def change_target_value_to_str(target_value, target_type, sub_type=None):
        if target_type in ('list', 'files'):
            return ','.join([str(_) for _ in target_value])
        elif target_type == 'dict':
            return ','.join([f'{k}:{v}' for k, v in target_value.items()])
        elif target_type == 'kv':
            for k, v in sub_type.items():
                if v == target_type:
                    return k
            else:
                return target_value
        elif target_type == 'json':
            return json.dumps(target_value)
        elif target_type == 'byte':
            temp_list = []
            now_value = int(target_value)
            while now_value > 0:
                temp_value = now_value % 1024
                now_value = (now_value - temp_value) // 1024
                temp_list.insert(0, str(temp_value))
            return '.'.join(temp_list)
        else:
            return str(target_value)

    def param_read(self):
        for one_param in self._origin_list:
            param_type, param_key, param_index = one_param[:3]
            param_text = ''
            if param_type == 'single':
                param_text = f'-{param_key}'
            elif param_type == 'full':
                param_text = f'--{param_key}'
            elif param_type == 'key':
                param_text = f'{param_key}={one_param[3]}'
            if param_key in self._config_key[param_type]:
                real_list = self._config_key[param_type][param_key]
                real_key = real_list[0]
                real_type = real_list[1:]
                param_count = self._config_dict[real_key]['param']
                try:
                    get_params = one_param[3] if param_type == 'key' else self.get_param(param_index, param_count)
                    self._value[real_key] = self.change_str_to_target_type(get_params, *real_type)
                except Exception as err:
                    raise Exception(f'{param_text} need input {param_count} param but {err}')

    def param_default(self):
        for i, v in self._config_dict.items():
            if i not in self._value and 'default' in v:
                self._value[i] = v['default']

    def param_check(self):
        for i, v in self._config_dict.items():
            if i not in self._value:
                if v['ask']:
                    self.param_ask(i)
                elif v['must']:
                    help_key = []
                    if 'single' in v:
                        help_key.append(f'-{v["single"]}')
                    if 'full' in v:
                        help_key.append(f'--{v["full"]}')
                    if 'key' in v:
                        help_key.append(f'{v["key"]}=?')
                    if 'ini' in v:
                        help_key.append(f'{v["ini"][0]}-{v["ini"][1]} in .ini')
                    raise Exception(f'you must config [{i}] by [{" ; ".join(help_key)}]')

    def param_pre_ask(self, key, target_type, sub_type=None):
        if target_type == 'file':
            title = self._config_dict[key].get('pre_ask_text', 'choose one file to input')
            input_file = filedialog.askopenfilename(title=title)
            return str(input_file)
        elif target_type == 'files':
            title = self._config_dict[key].get('pre_ask_text', 'choose files to input')
            input_file = filedialog.askopenfilenames(title=title)
            return ','.join(input_file)
        elif target_type == 'dir':
            title = self._config_dict[key].get('pre_ask_text', 'choose one folder to input')
            input_file = filedialog.askdirectory(title=title)
            return str(input_file)

    def param_ask(self, key):
        while True:
            pre_input = self.param_pre_ask(key, *self._config_dict[key]['type_list'])
            if pre_input:
                input_str = pre_input
            else:
                if self._config_dict[key]['type'] in ('file', 'files', 'dir'):
                    input_ask = f"please input path to config [{key}], or input nothing to choose in dialog window:"
                elif self._config_dict[key]['type'] == 'enum':
                    input_ask = f"please input (enum)[" + ', '.join([f"{i + 1}.{v}" for i, v in enumerate(self._config_dict[key]['sub'])]) + "] to config [{key}]:"
                else:
                    input_ask = f"please input {self._config_dict[key]['type_list']} to config [{key}]:"
                input_str = input(self._config_dict[key].get('ask_text', input_ask))
            try:
                self._value[key] = self.change_str_to_target_type(input_str, *self._config_dict[key]['type_list'])
                print(f'set <{key}> to <{self._value[key]}>')
                break
            except Exception as err:
                print(f'something wrong happened,please input again:{err}')
                continue

    def read_file(self, file=None):
        if file is not None:
            self._config_file = file
        if self._config_file is not None:
            config_path = Path(self._config_file)
            if config_path.exists():
                cf = ConfigParser()
                cf.read(config_path)
                for i_section in cf.sections():
                    v_section = cf[i_section]
                    for i_option, v_option in v_section.items():
                        ini_key = (i_section, i_option)
                        if ini_key in self._config_key['ini']:
                            key_list = self._config_key['ini'][ini_key]
                            real_key = key_list[0]
                            real_type = key_list[1:]
                            if self._config_dict[real_key]['config']:
                                self._value[real_key] = self.change_str_to_target_type(v_option, *real_type)

    def write_file(self, file=None):
        if file is not None:
            self._config_file = file
        if self._config_file is not None:
            config_path = Path(self._config_file)
            cf = ConfigParser()
            for i, v in self._value.items():
                if self._config_dict[i]['config']:
                    section, option = self._config_dict[i]['ini']
                    value = self.change_target_value_to_str(v, *self._config_dict[i]['type_list'])
                    if not cf.has_section(section):
                        cf.add_section(section)
                    cf.set(section, option, value)
            with config_path.open(mode='w') as config_file:
                cf.write(config_file)

    def show_all(self, unset=False):
        print(f'config value is shown as below (unset will {"not " if not unset else ""}show):')
        unset_list = []
        for key, config_dict in self._config_dict.items():
            if key in self._value:
                value = self._value[key]
                type_list = config_dict['type_list']
                print(f'{key} ({config_dict["type"]}) = {self.change_target_value_to_str(value, *type_list)}')
            else:
                unset_list.append(key)
        if unset:
            print(f'<{",".join(unset_list)}> did not set yet')
