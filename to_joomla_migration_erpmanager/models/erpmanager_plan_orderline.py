from odoo import models, fields


class ERPManagerPlanOrderLine(models.TransientModel):
    _name = 'erpmanager.plan.orderline'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Plan Order Line'
    _joomla_table = 'erpmanager_plan_orderline'

    joomla_id = False
    saleorder_id = fields.Many2one('erpmanager.saleorder', joomla_column=True)
    plan_id = fields.Many2one('erpmanager.plan', joomla_column=True)
    unitprice = fields.Integer(joomla_column=True)
    currency_id = fields.Many2one('erpmanager.currency', joomla_column=True)
    odoo_id = fields.Many2one('sale.order.line')
