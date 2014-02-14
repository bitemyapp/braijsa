import os

identity = lambda x: x

def kgetter(inst, key):
    if isinstance(inst, dict):
        return inst.get(key)
    elif isinstance(inst, identity.__class__):
        return inst(key)
    else:
        raise Exception("type error, inst not dict or func")

def vals_from_stores(key, stores):
    return map(lambda x: kgetter(x, key), stores)

def some(coll):
    return filter(identity, coll)

def last_truthy(coll):
    return some(coll)[-1]

def fallback(key, stores):
    return last_truthy(vals_from_stores(key, stores))

config_defaults = {"berossus_url": "http://localhost:3000/api/v1/braijsa_test/",
                   "client_id": "admin",
                   "token": "booya",
                   "service_url":  "http://localhost:3000/api/v1/services/braijsa_test/"}

class Config(object):
    def __init__(self, overrides={}, defaults=config_defaults):
        assert isinstance(defaults, dict)
        assert isinstance(overrides, dict)
        stores = [config_defaults, os.getenv, overrides]
        for key in defaults:
            val = fallback(key, stores)
            setattr(self, key, val)
