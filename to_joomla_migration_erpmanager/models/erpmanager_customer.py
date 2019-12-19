from odoo import models, fields


class ERPManagerCustomer(models.TransientModel):
    _name = 'erpmanager.customer'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Customer'
    _joomla_table = 'erpmanager_customer'

    partner_id = fields.Many2one('erpmanager.partner', joomla_column=True)
    odoo_id = fields.Many2one('res.partner', related='partner_id.odoo_id')
