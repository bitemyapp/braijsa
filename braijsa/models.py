from bottom.berossus import query
from braijsa import Config
from edn_format import ImmutableDict, dumps, loads
from util import add, comp, concat, cond_apply, dubs, \
     ffirst, K, left, nth, par, rewrite_dict, right, S, \
     selector_to_dict, tuple_comb


field_ignores = {u'add', u'app_id', u'cardinality', u'code', u'doc', u'excise', u'fn', u'fulltext', u'ident', u'index', u'install', u'isComponent', u'lang', u'noHistory', u'part', u'project', u'retract', u'tag', u'txInstant', u'type', u'unique', u'valueType'}
model_ignores = {"db", "fressian", "Entity"}
value_ignores = {None, u'uri', u'float', u'valueType', u'user', u'boolean', u'noHistory', u'valueType', u'function', u'ident', u'attribute', u'one', u'bigdec', u'java', u'beforeT', u'tag', u'retractEntity', u'clojure', u'fn', u'bigint', u'lang', u'ref', u'bytes', u'identity', u'partition', u'txInstant', u'index', u'fn', u'unique', u'before', u'keyword', u'attrs', u'doc', u'isComponent', u'cardinality', u'double', u'app_id', u'long', u'db', u'string', u'retract', u'code', u'instant', u'add', u'value', u'excise', u'many', u'fulltext', u'tx', u'cas'}

def query_fn(url, transactee, params=[], limit=20, offset=0):
    return query(url, transactee, params=params, limit=limit, offset=offset,
                 client_id=Config().client_id, token=Config().token)

def query_with_constraints(nouns, constraints, param_labels=None):
    """ nouns : [S|K], constraints : [[e a v & ...]] """
    partial = [K("find")] + nouns
    if param_labels:
        partial += [K("in"), S("$")] + param_labels
    partial += ([K("where")] + constraints)
    return partial

def sanitize_attributes(attributes):
    return map(lambda x: x[0], attributes.get(K("result")))

def query_attributes(url, limit=10000):
    e = S("?e")
    a = K("db/ident")
    v = S("?v")
    return query_fn(url, query_with_constraints([v], [[e, a, v]]), limit=limit)

def split_by_namespace(attribute):
    return attribute._name.split("/")

def extract_left(attribute):
    return split_by_namespace(attribute)[:-1]

def get_attributes():
    return sanitize_attributes(query_attributes(Config().berossus_url))

def extract_model(attribute):
    return extract_left(attribute)[0].split(".")[0]

def get_models(ignore=model_ignores):
    return set(map(extract_model, get_attributes())).difference(ignore)

def extract_field(attribute):
    if '.' in attribute._name:
        exd = extract_left(attribute)[0].split(".")
    else:
        exd = attribute._name.split("/")
    if len(exd) > 1:
        return exd[1]
    else:
        return None

def get_fields(ignore=field_ignores):
    return set(map(extract_field, get_attributes())).difference(ignore)

def extract_value(field, attribute):
    if '.' in attribute._name and extract_field(attribute) == field:
        return split_by_namespace(attribute)[-1]
    else:
        return None

def get_values_for_field(field, ignore=value_ignores):
    extract = par(extract_value, field)
    return set(map(extract, get_attributes())).difference(ignore)

def fields_for_model(model):
    return sorted(list(set(filter(lambda x: x,
                  map(extract_field,
                      filter(lambda x: extract_model(x) == model,
                             get_attributes()))))))

qify  = lambda x: "?" + x

def sym_to_str(sym):
    return str(sym)[1:]

def field_to_attribute(model, field):
    return model + "/" + field

# def instances_for_model(model, fields=None, limit=20, offset=0):
#     if not fields:
#         fields = fields_for_model(model)
#     # par is partial application, comp is function composition.
#     # left and right apply a function (first argument) to the
#     # left or right-hand side of a tuple (second argument)
#     add_entity_variable = par(add, (S("?e"),))
#     value_to_symbol = par(right, S)
#     prepend_value_with_qmark = par(right, qify)
#     attribute_to_keyword = par(left, K)
#     attribute_from_field = par(left, par(field_to_attribute, model))
#     constraints = map(comp(add_entity_variable, # ((Symbol("?e"), ...)
#                       value_to_symbol,
#                       prepend_value_with_qmark,
#                       attribute_to_keyword,
#                       attribute_from_field,
#                       dubs), 
#                 fields)
#     nouns = [S("?e")] + map(par(nth, 2), constraints)
#     assembled_query = query_with_constraints(nouns, constraints)
#     # given model "Message" with fields "message_type", "uuid", "timestamp",
#     # should get [(S("?e"),
#     #              K("Message/message_type"),
#     #              S("?message_type")) e.t.c.]
#     return query_fn(Config().berossus_url, assembled_query, limit=limit, offset=offset)

def get_entity(field):
    return [[S("get-entity"), S("?ent")],
            [S("?ent"), field, S("_")]]

def instances_for_model(model, fields=None, limit=20, offset=0):
    if not fields:
        fields = fields_for_model(model)
    attribute_from_field = par(field_to_attribute, model)
    keywordify = comp(K, attribute_from_field)
    entity_from_field = comp(get_entity, keywordify)
    rules = map(entity_from_field, fields)
    query = [K("find"), S("?e"), S("?touched"), K("in"), S("$"), S("%"),
             K("where"), S("(get-entity ?eid)"),
                          [S("(datomic.api/entity $ ?eid)"), S("?e")],
                          [S("(datomic.api/touch ?e)"), S("?touched")]]
    import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(dumps(rules))
    pp.pprint(dumps(query))
    return query_fn(Config().berossus_url, query, params=[rules], limit=limit, offset=offset)

def values_for_instance(id):
    return query_fn(Config().berossus_url,
                 [K("find"), S("?s"), K("in"), S("$"), S("?e"),
                  K("where"),
                  [S("(datomic.api/entity $ ?e)"), S("?ent")],
                  [S("(datomic.api/touch ?ent)"), S("?s")]],
                  params=[id])

def ident_for_id(id):
    return query_fn(Config().berossus_url,
                 [K("find"), S("?id"), K("in"), S("$"), S("?e"),
                  K("where"), [S("?e"), K("db/ident"), S("?id")]],
                  params = [id])

def grab_single(result):
    return comp(ffirst, par(nth, K("result")))(result)

def instance_for_ident(ident):
    find = [S("?s")]
    constraints = [[S("?e"), K("db/ident"), S("?ident")],
                   [S("(datomic.api/entity $ ?e)"), S("?ent")],
                   [S("(datomic.api/touch ?ent)"), S("?s")]]
    transactee = query_with_constraints(find, constraints, param_labels=[S("?ident")])
    return query_fn(Config().berossus_url, transactee, params=[ident])

def field_instances_for_model(model):
    attributes = map(par(field_to_attribute, model), fields_for_model(model))
    return map(comp(grab_single, instance_for_ident), attributes)

def keywordp(k):
    return type(k) == K

def keyword_to_str(k):
    return k._name

def stringify_keywords(d):
    return rewrite_dict(d, tuple_comb(*list(dubs(par(cond_apply, keywordp, keyword_to_str)))))

def field_instances_for_model_s(model):
    return map(stringify_keywords, field_instances_for_model(model))

# Fakey, but it suffices.
db_id_instance = {"db/cardinality": "db.cardinality/one",
                  "db/ident": "db/id",
                  "db/valueType": "db.type/long"}

def keyed_field_instances_for_model_s(model):
    keyed = selector_to_dict(field_instances_for_model_s(model), "db/ident")
    keyed['db/id'] = db_id_instance
    return keyed
