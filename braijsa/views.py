from flask import g, jsonify, redirect, render_template, request, session, url_for
# import forms
import models
from server import app
from util import comp, cond_apply, get, K, left, lwrap, par, S

class Item(object):
    def __init__(self, data, url=None, label=None):
        self.data = data
        self.url = url
        self.label = label or data

    def __repr__(self):
        return "<Item url: " + self.url + " data: " + self.data + " label: " + self.label + ">"

@app.route('/')
def index():
    page_desc = "Home"
    headers = map(Item, ["Model name"])
    data = map(lambda x: Item(x, url="/list/" + x, label=x),
               models.get_models())
    return render_template('index.html', **locals())

def get_offset(page, limit):
    return (page * limit) - limit

def paginate(request, limit=20):
    page  = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', limit))
    offset = get_offset(page, limit)
    return (page, limit, offset)

def navigate_pages(count, limit, page):
    prev_page = page - 1
    next_page = page + 1
    if page == 1:
        prev_page = False
    if count - (page * limit) < limit:
        next_page = False
    last_page = count / limit
    return (prev_page, next_page, last_page)

def paired_field_to_attribute(model, pair):
    """ "Message", ("message_type", 234925093459) =>
                   ("Message/message_type", 234925093459) """
    field, value = pair
    return (model + "/" + field, value)

def item_given_metadata(model, attr_metadata, pair):
    attributed = paired_field_to_attribute(model, pair)
    attribute, value = attributed
    this_attr_metadata = attr_metadata[attribute]
    db_type = this_attr_metadata["db/valueType"]
    is_ref = db_type == "db.type/ref"
    url = None
    if (attribute == "db/id" or is_ref) and value is not None and type(value) is int:
        url = url_for("instance", id=value)
    return Item(value, url=url)

@app.route('/list/<model>')
def model_instances(model):
    page, limit, offset = paginate(request)
    page_desc = "Listing of " + model + " instances"
    breadcrumbs = [("Home", url_for("index"))]
    fields = models.fields_for_model(model)
    fields_plus = ["db/id"] + fields
    attributes = ["db/id"] + map(par(models.field_to_attribute, model), fields)
    headers = map(Item, fields_plus) # [Item("id")] + 
    results = models.instances_for_model(model, fields, limit=limit, offset=offset)
    instances = results[K("result")]
    count = results[K("count")]
    prev_page, next_page, last_page = navigate_pages(count, limit, page)
    # fields and their metadata keyed by stringly db/ident
    attr_metadata = models.keyed_field_instances_for_model_s(model)
    data = []
    for instance in instances:
        row = []
        for field in attributes:
            stred = models.stringify_keywords(instance[0])
            pair = (field, stred.get(field))
            row.append(item_given_metadata(model, attr_metadata, pair))
        data.append(row)
    return render_template('table.html', **locals())

@app.route('/view/<int:id>')
def instance(id):
    page_desc = "Viewing instance id: " + str(id)
    extra_bc = request.args.get("breadcrumb")
    breadcrumbs = [("Home", url_for("index"))]
    if extra_bc:
        breadcrumbs.append(extra_bc)
    this = models.values_for_instance(id)[K("result")][0][0]
    fields = this.keys()
    headers = map(comp(Item, str), fields)
    getter = par(get, this)
    data = [map(comp(Item, getter), fields)]
    return render_template('table.html', **locals())
