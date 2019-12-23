from odoo import models, fields


class ERPManagerPlan(models.TransientModel):
    _name = 'erpmanager.plan'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Plan'
    _joomla_table = 'erpmanager_plan'

    name = fields.Char(joomla_column='title')
    max_bwpermonth = fields.Float(joomla_column=True)
    max_uaccounts = fields.Integer(joomla_column=True)
    max_backup = fields.Integer(joomla_column=True)
    max_spacesize = fields.Float(joomla_column=True)
    allow_custommodule = fields.Boolean(joomla_column=True)
    istrial = fields.Boolean(joomla_column=True)
    isaddon = fields.Boolean(joomla_column=True)
    odoo_id = fields.Many2one('product.product')

    def _get_matching_data(self, odoo_model):
        data = super(ERPManagerPlan, self)._get_matching_data()
        migration = self._get_current_migration()
        for item in migration.plan_map_ids:
            if item.joomla_plan_id not in data and item.odoo_product_id:
                data[item.joomla_plan_id] = item.odoo_product_id
        return data

    def _prepare_product_template_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            type='service',
            taxes_id=[],
            is_odoo_plan=True,
            is_addon=self.isaddon,
            max_bandwidth=self.max_bwpermonth,
            max_uaccounts=self.max_uaccounts,
            max_backups=self.max_backup,
            max_storage=self.max_spacesize,
            allow_custom_modules=self.allow_custommodule
        )
        return values

    def _migrate(self):
        self.ensure_one()
        if self.istrial:
            return False
        values = self._prepare_product_template_values()
        plan = self.env['product.template'].create(values)
        plan.product_variant_id.update(self._prepare_track_values())
        return plan.product_variant_id
