import ast

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
    odoo_id = fields.Many2one('res.partner')

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
            login=self.username,
            email=self.email,
            website_id=self.migration_id.to_website_id.id,
            active=not self.block
        )
        if self.language_id:
            values.update(lang=self.language_id.code)
        return values

    def _get_matching_data(self, odoo_model):
        return {}

    def _migrate(self, user_map):
        self.ensure_one()
        values = self._prepare_odoo_user_values()
        partner = user_map.get(self)
        if partner:
            if partner.user_ids:
                return partner
            self._logger.info('create user from existing partner')
            values.update(partner_id=partner.id)
        user = self.env['res.users'].create(values)
        return user.partner_id

    def migrate(self):
        user_map = {r.joomla_user_id: r.odoo_partner_id for r in self.migration_id.user_map_ids}
        super(JoomlaUser, self).migrate(user_map)
