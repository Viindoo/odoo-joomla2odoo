from odoo import models, fields


class ERPManagerCountry(models.TransientModel):
    _name = 'erpmanager.country'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Country'
    _joomla_table = 'erpmanager_country'

    name = fields.Char(joomla_column='title')
    odoo_id = fields.Many2one('res.country', compute='_compute_country')

    def _compute_country(self):
        for country in self:
            country.odoo_id = self.env['res.country'].search([('name', '=', country.name)], limit=1)
