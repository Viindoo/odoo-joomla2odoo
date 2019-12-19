from odoo import models, fields


class ERPManagerCurrency(models.TransientModel):
    _name = 'erpmanager.currency'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Currency'
    _joomla_table = 'erpmanager_currency'

    name = fields.Char(joomla_column='code')
    odoo_id = fields.Many2one('res.currency', compute='_compute_res_currency')

    def _compute_res_currency(self):
        currencies = self.env['res.currency'].search([('name', 'in', self.mapped('name'))])
        for r in self:
            r.odoo_id = currencies.filtered(lambda c: c.name == r.name)[:1]