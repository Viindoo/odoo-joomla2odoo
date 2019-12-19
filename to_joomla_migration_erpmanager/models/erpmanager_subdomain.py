from odoo import models, fields


class ERPManagerSubdomain(models.TransientModel):
    _name = 'erpmanager.subdomain'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Subdomain'
    _joomla_table = 'erpmanager_subdomain'

    name = fields.Char(joomla_column=True)
    basedomain_id = fields.Many2one('erpmanager.basedomain', joomla_column=True)
    instance_id = fields.Many2one('erpmanager.instance', joomla_column=True)
    ip_ids = fields.Many2many('erpmanager.ip', joomla_relation='erpmanager_ip_subdomain_rel',
                              joomla_column1='subdomain_id', joomla_column2='ip_id', string='IPs')
    ip = fields.Char(compute='_compute_ip')
    odoo_id = fields.Many2one('dns.domain')

    def _compute_ip(self):
        for r in self:
            r.ip = r.instance_id.vserver_id.proxyserver_ids[:1].working_ip_id.name

    def _prepare_subdomain_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            zone_id=self.basedomain_id.odoo_id.id,
            ip=self.ip,
            primary=True,
            instance_id=self.instance_id.odoo_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_subdomain_values()
        domain = self.env['dns.domain'].with_context(dns_deploy=False).create(values)
        return domain
