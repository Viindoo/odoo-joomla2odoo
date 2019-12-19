import ast
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import pycompat


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
    odoo_id = fields.Many2one('res.users')

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

    def _get_matching_data(self, odoo_model):
        migration = self._get_current_migration()
        if migration:
            return {m.joomla_user_id: m.odoo_user_id for m in migration.user_map_ids}
        return {}

    def _migrate(self, existing_logins, email_partner_map):
        self.ensure_one()
        user = self.env['res.users']
        login = self.username
        if login in existing_logins:
            login = self.email
        if login in existing_logins:
            self._logger.warning('ignore, invalid login')
            return user
        values = self._prepare_odoo_user_values()
        values.update(login=login)

        partner = self.env['res.partner']
        partners = email_partner_map.get(self.email)
        if partners and len(partners) == 1:
            partner = partners[0]
        if partner:
            self._logger.info('create from existing partner')
            values.update(partner_id=partner.id)

        user = user.create(values)
        if self.block:
            user.active = False
        return user

    def migrate(self):
        partners = self.env['res.partner'].search([])
        email_partner_map = defaultdict(list)
        for partner in partners:
            if partner.email:
                email_partner_map[partner.email].append(partner)

        existing_users = self.env['res.users'].search([])
        existing_logins = {user.login for user in existing_users}

        super(JoomlaUser, self).migrate(existing_logins, email_partner_map)
