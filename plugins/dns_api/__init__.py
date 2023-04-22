import logging
from .main import ItemProvider
from .views import Handler
from .providers.gandi import *


logging.info('dns_api.__init__.py: dns_api loaded')
