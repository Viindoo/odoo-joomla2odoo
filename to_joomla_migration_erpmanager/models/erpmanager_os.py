from odoo import models, fields


class ERPManagerOS(models.TransientModel):
    _name = 'erpmanager.os'
    _inherit = 'abstract.joomla.model'
    _description = 'ERPManager OS'
    _joomla_table = 'erpmanager_os'

    name = fields.Char(joomla_column='title')
    version = fields.Char(joomla_column=True)
    odoo_id = fields.Many2one('server.os', compute='_compute_server_os')

    def _compute_server_os(self):
        for os in self:
            os.odoo_id = self.env['server.os'].search([
                ('name', 'ilike', os.name),
                ('os_version_id.name', '=', os. version)
            ], limit=1)
