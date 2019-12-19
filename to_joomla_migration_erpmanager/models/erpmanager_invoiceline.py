from odoo import models, fields


class ERPManagerInvoiceLine(models.TransientModel):
    _name = 'erpmanager.invoiceline'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Invoice Line'
    _joomla_table = 'erpmanager_invoiceline'

    history_id = fields.Many2one('erpmanager.instance.history', joomla_column=True)
    invoice_id = fields.Many2one('erpmanager.invoice', joomla_column=True)
    datestart = fields.Datetime(joomla_column=True)