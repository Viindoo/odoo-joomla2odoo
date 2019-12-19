from odoo import models, fields


class ERPManagerInstanceHistory(models.TransientModel):
    _name = 'erpmanager.instance.history'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Instance History'
    _joomla_table = 'erpmanager_instance_history'

    instance_id = fields.Many2one('erpmanager.instance', joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    destroyed = fields.Datetime(joomla_column=True)
    customer_id = fields.Many2one('erpmanager.customer', joomla_column=True)
    customerplan_ids = fields.Many2many('erpmanager.customerplan', compute='_compute_customerplan')
    instanceperm_id = fields.Many2one('erpmanager.instanceperm', joomla_column=True)
    odoo_id = fields.Many2one('odoo.instance.history')

    def _compute_customerplan(self):
        instanceplans = self.env['erpmanager.instanceplan'].search([])
        for r in self:
            r.customerplan_ids = instanceplans.filtered(lambda ip: ip.instance_history_id == r).mapped('customerplan_id')

    def _prepare_instance_history_values(self):
        self.ensure_one()
        values = dict(
            instanceperm_id=self.instanceperm_id.odoo_id.id,
            customer_plan_id=self.customerplan_ids[:1].odoo_id.id,
            start_date=self.created,
            destroy_date=self.destroyed
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        if not self.customerplan_ids:
            return False
        values = self._prepare_instance_history_values()
        history = self.env['odoo.instance.history'].create(values)
        return history
