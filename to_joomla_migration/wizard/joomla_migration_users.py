from collections import defaultdict

from odoo import models, fields


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_user = fields.Boolean(default=True, readonly=True)
    joomla_user_ids = fields.One2many('joomla.user', 'migration_id', string='Joomla Users')
    user_map_ids = fields.One2many('joomla.migration.user.map', 'migration_id')
    no_reset_password = fields.Boolean(string='No Reset Password', default=True, help="If checked, no reset password request will be raised")

    def action_view_user_map(self):
        return dict(
            name='User Map',
            type='ir.actions.act_window',
            res_model='joomla.migration.user.map',
            view_mode='tree',
            targe='new',
            domain='[("migration_id", "=", {})]'.format(self.id),
            context=dict(search_default_not_mapped=1)
        )

    def _get_joomla_models(self):
        jmodels = super(JoomlaMigration, self)._get_joomla_models()
        jmodels['joomla.user'] = 100
        return jmodels

    def _load_data(self):
        res = super(JoomlaMigration, self)._load_data()
        if self.include_user:
            self._init_user_map()
        return res

    def _init_user_map(self):
        user_map = self._get_user_map()
        for juser, partner in user_map.items():
            self.env['joomla.migration.user.map'].create({
                'migration_id': self.id,
                'joomla_user_id': juser.id,
                'odoo_partner_id': partner.id
            })

    def _get_user_map(self):
        user_map = {}
        email_to_partners = self._get_email_to_partners_map()
        for juser in self.joomla_user_ids:
            if juser.email:
                email = juser.email.strip().lower()
                partners = email_to_partners.get(email)
                if partners:
                    user_map[juser] = partners[0]
                else:
                    user_map[juser] = self.env['res.partner']
        return user_map

    def _get_email_to_partners_map(self):
        partners = self.env['res.partner'].search([])
        email_to_partners = defaultdict(list)
        for partner in partners:
            if partner.email:
                email = partner.email.strip().lower()
                if partner.is_company:
                    email_to_partners[email].insert(0, partner)
                else:
                    email_to_partners[email].append(partner)
        return email_to_partners

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_user:
            self.joomla_user_ids.with_context(no_reset_password=self.no_reset_password).migrate()


class UserMap(models.TransientModel):
    _name = 'joomla.migration.user.map'
    _description = 'User Migration Map'

    migration_id = fields.Many2one('joomla.migration', ondelete='cascade', required=True)
    joomla_user_id = fields.Many2one('joomla.user', ondelete='cascade', required=True)
    odoo_partner_id = fields.Many2one('res.partner', ondelete='cascade')
    odoo_partner_idx = fields.Integer(related='odoo_partner_id.id', string='Odoo Partner ID')
