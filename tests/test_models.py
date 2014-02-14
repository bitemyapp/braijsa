from bottom.models import Model
from bottom.fields import (RefField, CARD_MANY,
                           StringField, FloatField,
                           InstantField, UNIQUE_IDENTITY,
                           UNIQUE_VALUE, LongField,
                           UUIDField, BooleanField,
                           DoubleField, EnumField)
from braijsa.util import K
from datetime import datetime
from edn_format import loads
import pytz
import random
import uuid

class Entity(Model):
	app_id = StringField(unique=UNIQUE_VALUE)
	project = RefField(refers_to="Project", cardinality=CARD_MANY)

	@classmethod
	def create(cls, datastore, **kwargs):
		new_obj = cls(**kwargs)
		datastore.save(new_obj)
		new_obj._datastore = datastore
		return new_obj

	def save(self):
		return self._datastore.save(self)

class Message(Entity):
    uuid = UUIDField()
    message_type = EnumField(enums=(("update", "Update message"),
                                    ("create", "Create message")))
    timestamp = InstantField()

def generate_uuid():
    return loads("#uuid \"%s\"" % uuid.uuid1())

def generate_enum(model, field, vals):
    return K("%s.%s/%s" % (model, field, random.choice(vals)))

def generate_instant(start_date=None, end_date=None):
    if not start_date:
        start_date = datetime.today().replace(day=1, month=1).toordinal()
    if not end_date:
        end_date = datetime.today().toordinal()
    return pytz.utc.localize(datetime.fromordinal(random.randint(start_date, end_date)))

def inject_id(d, dbid=loads("#db/id[:db.part/user]")):
    d[K("db/id")] = dbid
    return d

def generate_message():
    message_type = generate_enum("Message", "message_type", ["update", "create"])
    return inject_id({K("Message/uuid"): generate_uuid(),
                      K("Message/message_type"): message_type,
                      K("Message/timestamp"): generate_instant()})
