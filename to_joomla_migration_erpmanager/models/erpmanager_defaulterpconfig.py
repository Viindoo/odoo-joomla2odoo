from odoo import models, fields


class ERPManagerDefaultERPConfig(models.TransientModel):
    _name = 'erpmanager.defaulterpconfig'
    _inherit = 'abstract.erpmanager.erpconfig'
    _description = 'ERPManager Default ERP Config'
    _joomla_table = 'erpmanager_defaulterpconfig'

    erpversion_id = fields.Many2one('erpmanager.erpversion', joomla_column=True)
    odoo_id = fields.Many2one('odoo.version.config')

    def _prepare_odoo_version_config_values(self):
        self.ensure_one()
        values = self._prepare_config_values()
        values.update(
            odoo_version_id=self.erpversion_id.odoo_id.id
        )
        return values

    def _migrate(self):
        self.ensure_one()
        if self.erpversion_id.name == '7.0.0':
            return False
        values = self._prepare_odoo_version_config_values()
        config = self.env['odoo.version.config'].create(values)
        return config
