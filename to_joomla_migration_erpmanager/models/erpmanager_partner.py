from odoo import models, fields


class ERPManagerPartner(models.TransientModel):
    _name = 'erpmanager.partner'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Partner'
    _joomla_table = 'erpmanager_partner'

    uid = fields.Many2one('joomla.user', joomla_column=True)
    company_name = fields.Char(joomla_column=True)
    odoo_id = fields.Many2one('res.partner', related='uid.odoo_id')
