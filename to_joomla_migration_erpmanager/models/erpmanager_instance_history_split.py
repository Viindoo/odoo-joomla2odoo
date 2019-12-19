from odoo import models, fields


class ERPManagerInstanceHistorySplit(models.TransientModel):
    _name = 'erpmanager.instance.history.split'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Instance History Split'
    _joomla_table = 'erpmanager_instance_history_split'

    joomla_id = False
    instance_history_id = fields.Many2one('erpmanager.instance.history', joomla_column=True)
    datestart = fields.Datetime(joomla_column=True)
    dateend = fields.Datetime(joomla_column=True)
    invoiced = fields.Boolean(compute='_compute_invoiced')
    odoo_id = fields.Many2one('odoo.instance.history.split')

    def _compute_invoiced(self):
        invoice_lines = self.env['erpmanager.invoiceline'].search([])
        history_datestart = set((line.history_id, line.datestart) for line in invoice_lines)
        for split in self:
            split.invoiced = (split.instance_history_id, split.datestart) in history_datestart

    def _prepare_history_split_values(self):
        self.ensure_one()
        values = dict(
            history_id=self.instance_history_id.odoo_id.id,
            start_date=self.datestart,
            end_date=self.dateend,
            invoiced=self.invoiced
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        if not self.instance_history_id.customerplan_ids:
            return False
        values = self._prepare_history_split_values()
        split = self.env['odoo.instance.history.split'].create(values)
        return split
