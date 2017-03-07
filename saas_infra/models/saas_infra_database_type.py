# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
# from openerp.exceptions import ValidationError


class SaasInfraDatabaseType(models.Model):

    _name = 'saas.infra.database_type'
    _description = 'Odoo Saas Infra Database Type'
    _order = 'sequence'

    sequence = fields.Integer(
        default=10,
    )
    name = fields.Char(
        required=True
    )
    description = fields.Text(
    )
    domain = fields.Char(
        required=True,
        help='This domain will be used to generate subdomains for databases'
    )
    schema = fields.Selection(
        [('http', 'http'), ('https', 'https')],
        required=True,
    )
    rancher_environment_id = fields.Many2one(
        'saas.infra.rancher.environment',
        required=True
    )
