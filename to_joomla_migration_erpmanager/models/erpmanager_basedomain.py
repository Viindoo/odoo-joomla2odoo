import os

from odoo import models, fields


class ERPManagerBasedomain(models.TransientModel):
    _name = 'erpmanager.basedomain'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Basedomain'
    _joomla_table = 'erpmanager_basedomain'

    name = fields.Char(joomla_column=True)
    description = fields.Text(joomla_column=True)
    dnsserver_id = fields.Many2one('erpmanager.dnsserver', joomla_column=True)
    forward_ip = fields.Char(joomla_column=True)
    forwdzone_file = fields.Char(joomla_column=True)
    ssl_certificate = fields.Text(joomla_column=True)
    ssl_certificate_key = fields.Text(joomla_column=True)
    admin_only = fields.Boolean(joomla_column=True)
    odoo_id = fields.Many2one('dns.zone')

    def _prepare_basedomain_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            mname='ns1.{}'.format(self.name),
            email='hostmaster@' + self.name,
            forward_ip=self.forward_ip,
            zone_file_name=os.path.basename(self.forwdzone_file),
            description=self.description,
            dns_server_id=self.dnsserver_id.odoo_id.id,
            admin_only=self.admin_only
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        if self.ssl_certificate:
            cert_values = self._prepare_ssl_certificate_values(self.name, self.ssl_certificate, self.ssl_certificate_key)
            self.env['ssl.certificate'].create(cert_values)
        values = self._prepare_basedomain_values()
        basedomain = self.env['dns.zone'].create(values)
        return basedomain
