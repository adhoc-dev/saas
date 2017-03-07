# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
# from fabric.contrib.files import exists, append, sed
import logging
_logger = logging.getLogger(__name__)


class SaasInfraRancherEnvironment(models.Model):
    _name = 'saas.infra.rancher.environment'
    _description = 'Odoo Saas Infra Rancher Environment'

    name = fields.Char(
        required=True,
    )
    url = fields.Char(
        required=True,
        help='URL of the API. For eg: "http://localhost:8080/v1"'
    )
    access_key = fields.Char(
        required=True,
        help='Access Key. For eg: "4C27AB31828A4E469C09"'
    )
    secret_key = fields.Char(
        required=True,
        help='Secret Key. For eg: "fDxEzyxdFMWbmugstPpzykj2qA84Tn9DPDiAc3Sb"'
    )
