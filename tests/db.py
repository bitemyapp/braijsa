from bottom.berossus import transact, delete_service, create_service
from bottom.datastore import models_to_schema_edn
from braijsa import Config
import edn_format
import requests
from test_models import Message, generate_message
from braijsa.util import jfdi, n_times, par

def transact_fn(*args, **kwargs):
    kwargs['client_id'] = Config().client_id
    kwargs['token'] = Config().token
    return transact(*args, **kwargs)

def transact_schema(db_url):
    return transact_fn(db_url, models_to_schema_edn([Message]))

def bootstrap_schema(config, backend_uri):
    client_id = Config().client_id
    token = Config().token
    jfdi(delete_service, [config.service_url], {'client_id': client_id, 'token': token})
    create_service(config.service_url, backend_uri, client_id=client_id, token=token)
    return transact_schema(config.berossus_url)

def bootstrap_fixtures(config, backend_uri, fixtures=["./tests/fixtures/messages.edn"]):
    bootstrap_schema(config, backend_uri)
    parsed_fixtures = []
    for fixture in fixtures:
        parsed = edn_format.loads(open(fixture).read())
        parsed_fixtures += parsed
    return transact_fn(config.berossus_url, parsed_fixtures)

def bootstrap_generators(config, backend_uri, generators):
    bootstrap_schema(config, backend_uri)
    instances = []
    for generator in generators:
        instances += generator()
    return transact_fn(config.berossus_url, instances)

if __name__ == "__main__":
    # "http://localhost:3000/api/v1/service/braijsa_test/"
    # print bootstrap_fixtures(Config(), "datomic:mem://braijsa_test")
    print bootstrap_generators(Config(), "datomic:mem://braijsa_test",
                               [par(n_times, 100, generate_message)])
