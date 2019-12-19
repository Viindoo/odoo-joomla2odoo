from odoo import models, fields


class ERPManagerDNSServer(models.TransientModel):
    _name = 'erpmanager.dnsserver'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager DNS Server'
    _joomla_table = 'erpmanager_dnsserver'

    name = fields.Char(joomla_column='title')
    pserver_id = fields.Many2one('erpmanager.pserver', joomla_column=True)
    bind9_dir = fields.Char(joomla_column=True)
    forwdzones_dir = fields.Char(joomla_column=True)
    revzones_dir = fields.Char(joomla_column=True)
    zone_file = fields.Char(joomla_column=True)
    odoo_id = fields.Many2one('server.dns')

    def _prepare_server_dns_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            service_name='bind9',
            pserver_id=self.pserver_id.odoo_id.id,
            bind9_dir=self.bind9_dir,
            zones_file=self.zone_file,
            forwdzones_dir=self.forwdzones_dir,
            revzones_dir=self.revzones_dir
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_server_dns_values()
        server = self.env['server.dns'].create(values)
        return server
