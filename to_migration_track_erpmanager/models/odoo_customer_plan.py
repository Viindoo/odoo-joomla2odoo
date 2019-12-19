from odoo import models


class OdooCustomerPlan(models.Model):
    _name = 'odoo.customer.plan'
    _inherit = ['odoo.customer.plan', 'abstract.joomla.migration.track']
