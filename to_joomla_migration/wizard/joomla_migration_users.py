from odoo import models, fields


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_user = fields.Boolean(default=True, readonly=True)
    joomla_user_ids = fields.One2many('joomla.user', 'migration_id', string='Joomla Users')
    user_map_ids = fields.One2many('joomla.migration.user.map', 'migration_id')
    no_reset_password = fields.Boolean(string='No Reset Password', default=True, help="If checked, no reset password request will be raised")

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
        odoo_users = self.env['res.users'].search([])
        email_user_map = {r.email: r for r in odoo_users}
        for joomla_user in self.joomla_user_ids:
            odoo_user = email_user_map.get(joomla_user.email)
            if odoo_user:
                self.env['joomla.migration.user.map'].create({
                    'migration_id': self.id,
                    'joomla_user_id': joomla_user.id,
                    'odoo_user_id': odoo_user.id
                })

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_user:
            self.joomla_user_ids.with_context(no_reset_password=self.no_reset_password).migrate()


class UserMap(models.TransientModel):
    _name = 'joomla.migration.user.map'
    _description = 'User Migration Map'

    migration_id = fields.Many2one('joomla.migration', ondelete='cascade')
    joomla_user_id = fields.Many2one('joomla.user', ondelete='cascade')
    odoo_user_id = fields.Many2one('res.users', ondelete='cascade')
