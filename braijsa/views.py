from flask import g, jsonify, redirect, render_template, request, session, url_for
# import forms
import models
from server import app
from util import comp, get, K, lwrap, par, S

class Item(object):
    def __init__(self, data, url=None, label=None):
        self.data = data
        self.url = url
        self.label = label or data

def url(prefix, item, getter="data"):
    item.url = prefix + getattr(item, getter)
    return item

def add_fields(model_row):
    model_row.append(models.fields_for_model(model_row[0]))
    return model_row

@app.route('/')
def index():
    page_desc = "Listing of models we can find in the database"
    headers = map(Item, ["Model name", "Fields"])
    comped = comp(add_fields, par(map, comp(par(url, "/list/"), Item)), lwrap)
    data = map(comped, models.get_models())
    return render_template('table.html', **locals())

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

# def item_given_metadata(field_meta, value):
#     if 
#     return Item(value)
@app.route('/list/<model>')
def model_instances(model):
    page, limit, offset = paginate(request)
    page_desc = "Listing of " + model + " instances"
    breadcrumbs = [("Home", url_for("index"))]
    fields = models.fields_for_model(model)
    fields_plus = ["db/id"] + fields
    headers = map(Item, fields_plus) # [Item("id")] + 
    results = models.instances_for_model(model, fields, limit=limit, offset=offset)
    instances = results[K("result")]
    count = results[K("count")]
    prev_page, next_page, last_page = navigate_pages(count, limit, page)
    data = map(par(map, Item), instances)
    return render_template('table.html', **locals())

@app.route('/view/<int:id>')
def instance(id):
    page_desc = "Viewing instance id: " + str(id)
    breadcrumbs = [("Home", url_for("index"))]
    this = models.values_for_instance(id)[K("result")][0][0]
    fields = this.keys()
    headers = map(comp(Item, str), fields)
    getter = par(get, this)
    data = [map(comp(Item, getter), fields)]
    return render_template('table.html', **locals())
