from odoo import models, fields


class ERPManagerBlockedSubdomain(models.TransientModel):
    _name = 'erpmanager.blockedsubdomain'
    _inherit = 'abstract.erpmanager.model',
    _description = 'ERPManager Blocked Subdomain'
    _joomla_table = 'erpmanager_blockedsubdomain'

    name = fields.Char(joomla_column=True)
    basedomain_id = fields.Many2one('erpmanager.basedomain', joomla_column=True)
    odoo_id = fields.Many2one('blocked.domain.name')

    def _prepare_blocked_domain_name_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            zone_id=self.basedomain_id.odoo_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_blocked_domain_name_values()
        domain = self.env['blocked.domain.name'].create(values)
        return domain
