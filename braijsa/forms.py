from wtforms import Form, BooleanField, DateTimeField, DecimalField, \
     FloatField, IntegerField, TextField
from wtforms.validators import DataRequired

field_constructors = {"db.type/string": TextField,
                      "db.type/boolean": BooleanField,
                      "db.type/long": IntegerField,
                      "db.type/float": FloatField,
                      "db.type/bigdec": DecimalField,
                      "db.type/instant": DateTimeField,
                      "db.type/uuid": UUIDField,
                      "db.type/ref": ReferenceField,
                      "db.type/uri": URIField}

class FieldInfo(object):
    def __init__(self, data, meta, label, name):
        pass

def field_factory(form, field_meta, field_name, label, data):
    # blah.is_okay = BooleanField('Is this okay?', _form=blah, _name="is_okay")
    # blah.data = None
    return None

def form_factory(model, fields, values):
    instance = Form()
    return None
