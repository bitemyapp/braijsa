import functools as fn
from edn_format import Keyword, Symbol
from itertools import chain

def comp(*functions):
    return fn.reduce(lambda f, g: lambda x: f(g(x)), functions)

par      = fn.partial
identity = lambda x: x
lwrap    = lambda x: [x]
dubs     = lambda x: (x, x)
left     = lambda f, x: (f(x[0]), x[1])
right    = lambda f, x: (x[0], f(x[1]))
add      = lambda x, y: x + y
nth      = lambda n, x: x[n]
first    = par(nth, 0)
second   = par(nth, 1)
third    = par(nth, 2)
ffirst   = comp(first, first)
K        = Keyword
S        = Symbol
get      = lambda f, i: i[f]

def concat(*lists):
    return chain(lists)

def cond_apply(pred, f, datum):
    if pred(datum):
        return f(datum)
    else:
        return datum

def jfdi(fn, args, kwargs):
    try:
        fn(*args, **kwargs)
    except:
        pass

def n_times(num, fn):
    return [apply(fn) for _ in range(num)]

def selector_to_dict(coll, k):
    accum = {}
    for i in coll:
        key = i[k]
        accum[key] = i
    return accum

def tuple_comb(key_fn, val_fn):
    """ (a -> b) -> (c -> d) -> ((a, c) -> (b, d)) """
    def new_fn(pair):
        k, v = pair
        return (key_fn(k), val_fn(v))
    return new_fn

def rewrite_dict(d, rewriter):
    """ Map a b -> ((a, b) -> (c, d)) -> Map c d """
    fresh = {}
    for k in d:
        val = d[k]
        new_k, new_val = rewriter((k, val))
        fresh[new_k] = new_val
    return fresh

def rewrite_keys(d, key_fn):
    """ Map a b -> (a -> c) -> Map c b """
    return rewrite_dict(d, tuple_comb(key_fn, identity))
