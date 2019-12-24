from datetime import timedelta

from odoo import models, fields, api


class ERPManagerSaleOrder(models.TransientModel):
    _name = 'erpmanager.saleorder'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Sale Order'
    _joomla_table = 'erpmanager_saleorder'

    name = fields.Char(joomla_column='number')
    customer_id = fields.Many2one('erpmanager.customer', joomla_column=True)
    order_line_ids = fields.One2many('erpmanager.plan.orderline', 'saleorder_id')
    created = fields.Datetime(joomla_column=True)
    published = fields.Integer(joomla_column=True)
    currency_id = fields.Many2one('erpmanager.currency', joomla_column=True)
    state = fields.Char(compute='_compute_state')
    pricelist_id = fields.Many2one('product.pricelist', compute='_compute_pricelist')
    odoo_id = fields.Many2one('sale.order')

    @api.depends('published')
    def _compute_state(self):
        for r in self:
            if r.published == 0:
                r.state = 'draft'
            elif r.published == 1:
                r.state = 'sale'
            elif r.published == 2:
                r.state = 'done'
            else:
                r.state = 'cancel'

    @api.depends('currency_id', 'migration_id.pricelist_usd_id', 'migration_id.pricelist_vnd_id')
    def _compute_pricelist(self):
        for r in self:
            if r.currency_id.name == 'VND':
                r.pricelist_id = r.migration_id.pricelist_vnd_id
            else:
                r.pricelist_id = r.migration_id.pricelist_usd_id

    def _prepare_sale_order_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            partner_id=self.customer_id.odoo_id.id,
            state=self.state,
            pricelist_id=self.pricelist_id.id,
            date_order=self.created,
            validity_date=self.created + timedelta(days=30)
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_sale_order_values()
        order = self.env['sale.order'].create(values)
        for line in self.order_line_ids:
            values = line._prepapre_sale_order_line_values(order)
            for i in range(line.quantity):
                line.odoo_id = self.env['sale.order.line'].create(values)
        return order
