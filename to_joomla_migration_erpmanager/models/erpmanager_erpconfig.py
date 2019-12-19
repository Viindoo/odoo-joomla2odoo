from odoo import models, fields


class ERPManagerERPConfig(models.TransientModel):
    _name = 'erpmanager.erpconfig'
    _inherit = 'abstract.erpmanager.erpconfig'
    _description = 'ERPManager ERP Config'
    _joomla_table = 'erpmanager_erpconfig'

    oebackend_id = fields.Many2one('erpmanager.oebackend', joomla_column=True)
    defaulterpconfig_id = fields.Many2one('erpmanager.defaulterpconfig', joomla_column=True)
    odoo_id = fields.Many2one('odoo.instance.config')

    def _prepare_odoo_instance_config_values(self):
        self.ensure_one()
        values = self._prepare_config_values()
        values.update(
            instance_id=self.oebackend_id.instance_id.odoo_id.id,
            odoo_version_config_id=self.defaulterpconfig_id.odoo_id.id
        )
        return values

    def _migrate(self):
        self.ensure_one()
        if self.defaulterpconfig_id.erpversion_id.name == '7.0.0':
            return False
        values = self._prepare_odoo_instance_config_values()
        config = self.env['odoo.instance.config'].create(values)
        return config
