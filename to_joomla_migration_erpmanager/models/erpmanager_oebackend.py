from odoo import models, fields


class ERPManagerOEBackend(models.TransientModel):
    _name = 'erpmanager.oebackend'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager OEBackend'
    _joomla_table = 'erpmanager_oebackend'

    erpserver_id = fields.Many2one('erpmanager.erpserver', joomla_column=True)
    instance_id = fields.Many2one('erpmanager.instance', joomla_column=True)
