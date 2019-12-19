from odoo import models, fields


class ERPManagerERPVersion(models.TransientModel):
    _name = 'erpmanager.erpversion'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager ERP Version'
    _joomla_table = 'erpmanager_erpversion'

    name = fields.Char(joomla_column='version')
    odoo_id = fields.Many2one('odoo.version', compute='_compute_odoo_version')

    def _compute_odoo_version(self):
        for version in self:
            version.odoo_id = self.env['odoo.version'].search([('name', '=', version.name)], limit=1)
