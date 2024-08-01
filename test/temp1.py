from movoid_config import Config

config = Config({
    "param": {
        "type": "string",  # we will change it to a string.you can input: int,float,number,bool,true,false,list,dict,enum,kv,byte.others are all string.
        "default": "ppp",  # when you do not input,we will give a default value.it will make 'must' invalidate
        "single": "p",  # use like -p *
        "full": "param",  # use like --param *
        "key": "param",  # use like param=?
        "ini": ["main", "param"],  # use in config.ini
        "config": "True",  # whether try to find and write in .ini file
        "must": True,  # whether you must input it ,or it will raise exception
        "ask": True,  # when you do not input,you can change to ask user to input it
        "help": "This is param which is an example.",  # show it in help text.(not done yet)
    }
}, 'config.ini')
print(config.param)
