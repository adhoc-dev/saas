# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
# from fabric.contrib.files import exists, append, sed
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class database(models.Model):

    """"""
    _name = 'saas.infra.database'
    _description = 'Odoo Saas Infra Database'
    _inherit = ['ir.needaction_mixin', 'mail.thread']
    _states_ = [
        ('draft', 'Draft'),
        ('maintenance', 'Maintenance'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
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
    main_hostname = fields.Char(
        string='Main Hostname',
        requests=True,
    )
    # admin_password = fields.Char(
    #     string='Admin Password',
    #     help='When trying to connect to the database first we are going to '
    #     'try by using the instance password and then with thisone.',
    #     readonly=True,
    #     required=True,
    #     states={'draft': [('readonly', False)]},
    # )

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'Database Name Must be Unique'),
    ]

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise ValidationError(_(
                'You cannot delete a database which is not draft or cancelled')
            )
        return super(database, self).unlink()

    @api.one
    def create_db(self):
        """Funcion que utliza erpeek para crear bds"""
        _logger.info("Creating db '%s'" % (self.name))
        client = self.get_client(not_database=True)
        lang = self.instance_type_id.install_lang_id or 'en_US'
        if self.environment_id.odoo_version_id.name == '9.0':
            # improove this and make country code a parameter
            client.db.create_database(
                self.instance_id.admin_pass,
                self.name,
                self.demo_data,
                lang,
                self.admin_password or 'admin',
                'admin',
                'AR')
        else:
            # before v9 country_code was not a parameter
            client.create_database(
                self.instance_id.admin_pass,
                self.name,
                demo=self.demo_data,
                lang=lang,
                user_password=self.admin_password or 'admin')
        self.install_base_modules()
        # config backups
        self.config_backups()
        self.action_activate()

    @api.multi
    def drop_db(self):
        """Funcion que utiliza ws nativos de odoo para eliminar db"""
        self.ensure_one()
        by_pass_protection = self._context.get('by_pass_protection', False)
        if self.protected and not by_pass_protection:
            raise ValidationError(_(
                'You can not drop a database protected, '
                'you can change database type, or drop it manually'))
        _logger.info("Dropping db '%s'" % (self.name))
        sock = self.get_sock()
        try:
            sock.drop(self.instance_id.admin_pass, self.name)
        except:
            # If we get an error we try restarting the service
            try:
                self.instance_id.restart_odoo_service()
                # we ask again for sock and try to connect waiting for service
                # start
                sock = self.get_sock(max_attempts=1000)
                sock.drop(self.instance_id.admin_pass, self.name)
            except Exception, e:
                raise ValidationError(_(
                    'Unable to drop Database. If you are working in an '
                    'instance with "workers" then you can try '
                    'restarting service. This is what we get:\n%s') % (e))
        self.action_cancel()

    @api.multi
    def duplicate_db(self, new_database_name, backups_enable):
        """Funcion que utiliza ws nativos de odoo para hacer duplicar bd"""
        self.ensure_one()
        sock = self.get_sock()
        client = self.get_client()
        new_db = self.copy({
            'name': new_database_name,
            'backups_enable': backups_enable,
            'issue_date': fields.Date.today(),
            # 'database_type_id': database_type.id,
        })
        try:
            sock.duplicate_database(
                self.instance_id.admin_pass, self.name, new_database_name)
        except Exception, e:
            raise ValidationError(
                _('Unable to duplicate Database. This is what we get:\n%s') % (
                    e))
        client.model('db.database').backups_state(
            new_database_name, backups_enable)
        new_db.action_activate()
        if backups_enable:
            new_db.config_backups()
        # devolvemos la accion de la nueva bd creada
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')
        if not action:
            return False
        res = action.read()[0]
        # res['domain'] = [('id', 'in', databases.ids)]
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'infrastructure.view_infrastructure_database_form')
        res['views'] = [(form_view_id, 'form')]
        res['res_id'] = new_db.id
        return res

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

    @api.multi
    def action_inactive(self):
        self.write({'state': 'inactive'})
