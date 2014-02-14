from flask import Flask, g, session
# from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
ADMINS = ["cma@bitemyapp.com"]

app.config.from_object(__name__)
try:
    app.config.from_envvar('FLASK_SETTINGS')
except:
    app.config.from_pyfile('local_settings.cfg', silent=True)

# app.config['DATABASE_URI']
# if not app.debug:
#     sentry = Sentry(app)

from views import *

if __name__ == "__main__":
    app.run(host='0.0.0.0')
