from flask import Flask
from flask.logging import default_handler
import logging
from logging.config import dictConfig
from config import LOGGING
from models import start_db

dictConfig(LOGGING)
app = Flask(__name__)

app.logger = logging.getLogger('CurrencyMain')
app.logger.removeHandler(default_handler)

start_db()

import views