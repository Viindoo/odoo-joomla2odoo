import ast
import logging
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


class JoomlaUser(models.TransientModel):
    _name = 'joomla.user'
    _description = 'Joomla User'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'users'

    name = fields.Char(joomla_column=True)
    username = fields.Char(joomla_column=True)
    email = fields.Char(joomla_column=True)
    block = fields.Boolean(joomla_column=True)
    params = fields.Char(joomla_column=True)
    language_id = fields.Many2one('res.lang', compute='_compute_params_info')
    timezone = fields.Char(compute='_compute_params_info')
    odoo_user_id = fields.Many2one('res.users')

    @api.depends('params')
    def _compute_params_info(self):
        for user in self:
            params = ast.literal_eval(pycompat.to_native(user.params))
            user.language_id = self._get_lang_from_code(params.get('language'))
            user.timezone = params.get('timezone', '').replace('\\', '')

    def _prepare_odoo_user_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(
            name=self.name,
            tz=self.timezone or self.env.user.tz,
            groups_id=[(4, self.env.ref('base.group_portal').id)],
            login=self.name,
            email=self.email,
            website_id=self.migration_id.to_website_id.id
        )
        if self.language_id:
            values.update(lang=self.language_id.code)
        return values

    def _migrate(self, user_map, existing_logins, existing_email_partner_map):
        self.ensure_one()
        existing_user = user_map.get(self)
        existing_partner = self.env['res.partner']
        if not existing_user:
            partners = existing_email_partner_map.get(self.email)
            if partners and len(partners) == 1:
                existing_partner = partners[0]
        if not existing_user:
            login = self.username
            if login in existing_logins:
                login = self.email
            if login in existing_logins:
                _logger.info('ignore')
                return
            values = self.prepare_odoo_user_values()
            values.update(login=login)
            if existing_partner:
                values.update(partner_id=existing_partner.id,
                              created_from_existing_partner=True)
            existing_user = self.env['res.users'].create(values)
            if self.block:
                existing_user.active = False
            if existing_partner:
                _logger.info('created new user from existing partner')
            else:
                _logger.info('created new user')
        else:
            _logger.info('found matching user')
        self.odoo_user_id = existing_user.id

    def migrate(self, user_map):
        partners = self.env['res.partner'].search([])
        existing_email_partner_map = defaultdict(list)
        for partner in partners:
            if partner.email:
                existing_email_partner_map[partner.email].append(partner)

        existing_users = self.env['res.users'].search([])
        existing_logins = {user.login for user in existing_users}

        for idx, user in enumerate(self, start=1):
            _logger.info('[%s/%s] migrating user %s from the website %s' % (idx, len(self), user.username, user.migration_id.website_url))
            user._migrate(user_map, existing_logins, existing_email_partner_map)
            self.env.cr.commit()
