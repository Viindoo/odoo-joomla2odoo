from odoo import models, fields


class ERPManagerCustomerPlan(models.TransientModel):
    _name = 'erpmanager.customerplan'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Customer Plan'
    _joomla_table = 'erpmanager_customerplan'

    customer_id = fields.Many2one('erpmanager.customer', joomla_column=True)
    saleorder_id = fields.Many2one('erpmanager.saleorder', joomla_column=True)
    plan_id = fields.Many2one('erpmanager.plan', joomla_column=True)
    instance_id = fields.Many2one('erpmanager.instance', joomla_column=True)
    odoo_id = fields.Many2one('odoo.customer.plan')

    def _prepare_customer_plan_values(self):
        self.ensure_one()
        order_line = self.saleorder_id.order_line_ids.filtered(lambda line: line.plan_id == self.plan_id)
        assert order_line
        values = dict(
            sale_order_line_id=order_line.odoo_id.id,
            partner_id=self.customer_id.odoo_id.id,
            plan_id=self.plan_id.odoo_id.id,
            instance_id=self.instance_id.odoo_id.id,
            price=order_line.unitprice,
            currency_id=order_line.currency_id.odoo_id.id,
            max_bandwidth=self.plan_id.max_bwpermonth,
            max_uaccounts=self.plan_id.max_uaccounts,
            max_backups=self.plan_id.max_backup,
            max_storage=self.plan_id.max_spacesize,
            allow_custom_modules=self.plan_id.allow_custommodule
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one
        if not self.saleorder_id:
            return False
        values = self._prepare_customer_plan_values()
        cp = self.env['odoo.customer.plan'].create(values)
        return cp
