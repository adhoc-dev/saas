# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class SaasInfraDatabase(models.Model):

    """"""
    _name = 'saas.infra.database'
    _description = 'Odoo Saas Infra Database'
    _inherit = ['ir.needaction_mixin', 'mail.thread']
    _states_ = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('cancel', 'Cancel'),
    ]
    _mail_post_access = 'read'

    database_type_id = fields.Many2one(
        'saas.infra.database_type',
        string='Database Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
        copy=False,
    )
    database_type_domain = fields.Char(
        related='database_type_id.domain',
        readonly=True,
    )
    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange'
    )
    note = fields.Html(
        string='Note'
    )
    state = fields.Selection(
        _states_,
        'State',
        default='draft'
    )
    domain_prefix = fields.Char(
        required=True,
    )
    custom_domain = fields.Char(
        help='If you set a custom domain this one will be used as main domain.'
    )
    main_hostname = fields.Char(
        compute='_compute_main_hostname'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'Database Name Must be Unique'),
    ]

    @api.multi
    @api.depends('custom_domain', 'domain_prefix')
    def _compute_main_hostname(self):
        for rec in self:
            if rec.custom_domain:
                rec.main_hostname = rec.custom_domain
            else:
                rec.main_hostname = "%s.%s" % (
                    rec.domain_prefix, rec.database_type_domain)

    @api.multi
    @api.constrains('name')
    @api.onchange('name')
    def check_name(self):
        # TODO check that name only contains normal characters
        _logger.warning('Check name not implentend yet')

    @api.multi
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise ValidationError(_(
                'You cannot delete a database which is not draft or cancelled')
            )
        return super(SaasInfraDatabase, self).unlink()

    @api.multi
    def action_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_activate(self):
        self.write({'state': 'active'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})


# methods that communicate with rancher

    @api.multi
    def create_db(self):
        """
        Funcion que crea stack en rancher
        """
        self.ensure_one()
        _logger.info("Creating db '%s'" % (self.name))
        raise ValidationError(_('Not implemented yet'))
        # TODO completar con metodos
        # https://github.com/rancher/gdapi-python

        # self.action_activate()

    @api.multi
    def drop_db(self):
        """
        Funcion que elimina stack en rancher
        """
        self.ensure_one()
        _logger.info("Deleting db '%s'" % (self.name))
        raise ValidationError(_('Not implemented yet'))
        # TODO completar con metodos
        # https://github.com/rancher/gdapi-python

        # self.action_cancel()
