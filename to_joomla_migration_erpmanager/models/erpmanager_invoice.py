from odoo import models, fields


class ERPManagerInvoice(models.TransientModel):
    _name = 'erpmanager.invoice'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Invoice'
    _joomla_table = 'erpmanager_invoice'
