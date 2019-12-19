from odoo import models, fields


class ERPManagerInstancePlan(models.TransientModel):
    _name = 'erpmanager.instanceplan'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Instance Plan'
    _joomla_table = 'erpmanager_instanceplan'

    joomla_id = False
    instance_history_id = fields.Many2one('erpmanager.instance.history', joomla_column=True)
    saleorder_id = fields.Many2one('erpmanager.saleorder', joomla_column=True)
    plan_id = fields.Many2one('erpmanager.plan', joomla_column=True)
    customerplan_id = fields.Many2one('erpmanager.customerplan', joomla_column=True)
