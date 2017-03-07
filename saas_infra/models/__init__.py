# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from . import database
from . import database_type

# To avoid error with auto generated certificates:
try:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    print "Could not disable SSL checks on odoo infrastructure"
