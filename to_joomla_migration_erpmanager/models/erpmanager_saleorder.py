from odoo import models, fields


class ERPManagerSaleOrder(models.TransientModel):
    _name = 'erpmanager.saleorder'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Sale Order'
    _joomla_table = 'erpmanager_saleorder'

    name = fields.Char(joomla_column='number')
    order_line_ids = fields.One2many('erpmanager.plan.orderline', 'saleorder_id')
    odoo_id = fields.Many2one('sale.order')
