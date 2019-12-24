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
    quantity = fields.Integer(joomla_column=True)
    currency_id = fields.Many2one('erpmanager.currency', joomla_column=True)
    odoo_id = fields.Many2one('sale.order.line')

    def _prepapre_sale_order_line_values(self, order=None):
        self.ensure_one()
        values = dict(
            name=self.plan_id.odoo_id.name,
            order_id=order.id if order else self.saleorder_id.odoo_id.id,
            product_id=self.plan_id.odoo_id.id,
            product_uom_qty=1,
            price_unit=self.unitprice
        )
        return values;
