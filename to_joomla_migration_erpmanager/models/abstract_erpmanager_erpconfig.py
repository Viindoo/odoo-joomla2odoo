from odoo import models, fields


class AbstractERPManagerERPConfig(models.TransientModel):
    _name = 'abstract.erpmanager.erpconfig'
    _inherit = 'abstract.erpmanager.model'
    _description = 'Abstract ERPManager ERPConfig'

    name = fields.Char(joomla_column='key')
    value = fields.Char(joomla_column=True)
    section = fields.Char(joomla_column=True, string='Section Name')
    section_id = fields.Many2one('config.section', compute='_compute_config_section')

    def _compute_config_section(self):
        options = self.env.ref('to_odoo_version.config_section_options')
        saaslimits = self.env.ref('to_odoo_version.config_section_saaslimits')
        for config in self:
            if config.section == '[options]':
                config.section_id = options
            elif config.section == '[saaslimits]':
                config.section_id = saaslimits
            else:
                config.section_id = False

    def _prepare_config_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            value=self._get_deserialized_value(),
            section_id=self.section_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _get_deserialized_value(self):
        self.ensure_one()
        return self._deserialize_config_value(self.value)
