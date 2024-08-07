This is a simple program for developer to create a param-config reader.
It only needs config_dict and config_file_name to analyse all param and config

for example,your py file main.py is

```python
from movoid_config import Config

config = Config({
    "param": {
        "type": "string",  # we will change it to a string.you can input: int,float,number,bool,true,false,list,dict,enum,kv,byte.others are all string.
        "default": "ppp",  # when you do not input,we will give a default value.it will make 'must' invalidate
        "single": "p",  # use like -p *
        "full": "param",  # use like --param *
        "key": "param",  # use like param=?
        "ini": ["main", "param"],  # use in config.ini
        "config": True,  # whether try to find and write in .ini file
        "must": True,  # whether you must input it ,or it will raise exception
        "ask": True,  # when you do not input,you can change to ask user to input it
        "help": "This is param which is an example.",  # show it in help text.(not done yet)
    },
    "check": {
        "type": "true",
        "false": {
            "single": "f",
            "full": "false"
        }  # when type is true,you can input -f or --false to input a false value to "check"
    },
    "int_list": {
        "full": "list",
        "type": "list",
        "sub": "int"  # to define type of list value
    },
    "int_bool_dict": {
        "key": "dict",
        "type": "dict",
        "sub": ["int", "str"]  # to define type of dict key and value
    }
}, "config.ini")

print(config.param)
print(config["int_list"])
print(config["int_bool_dict"])

```

when you input 
```shell
python main.py -p p234 --list 1,2,3 dict=1:a,2:b
```
you can see 
```shell
p234
[1, 2, 3]
{1: 'a', 2: 'b'}
```

you can also use 
```python
from movoid_config import Config

config = Config({})
for i, v in config.items():
    print(i, v)
for i in config.keys():
    print(i)
for v in config.values():
    print(v)
```
to traversal loop

If you use when you do not input. An error will be raised like use an unknown key in a dict.
