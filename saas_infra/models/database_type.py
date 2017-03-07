# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
# from openerp.exceptions import ValidationError


class database_type(models.Model):

    _name = 'saas.infra.database_type'
    _description = 'Odoo Saas Infra Database Type'
    _order = 'sequence'

    sequence = fields.Integer(
        'Sequence',
        default=10,
    )
    name = fields.Char(
        string='Name',
        required=True
    )
    description = fields.Text(
        string='Description',
    )
