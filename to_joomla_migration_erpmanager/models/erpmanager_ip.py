from odoo import models, fields


class ERPManagerIP(models.TransientModel):
    _name = 'erpmanager.ip'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager IP'
    _joomla_table = 'erpmanager_ip'

    name = fields.Char(joomla_column='v4')
    for_managing = fields.Boolean(joomla_column=True)
    pserver_id = fields.Many2one('erpmanager.pserver', joomla_column=True)
    ip = fields.Many2one('server.ip', compute='_compute_ip')
    odoo_id = fields.Many2one('server.ip.line')

    def _compute_ip(self):
        IP = self.env['server.ip']
        ips = IP.search([])
        for r in self:
            ip = ips.filtered(lambda i: i.name == r.name)[:1]
            if not ip:
                ip = IP.create(dict(name=r.name))
                ips += ip
            r.ip = ip

    def _prepare_server_ip_line_values(self):
        self.ensure_one()
        values = dict(
            ip_id=self.ip.id,
            for_managing=self.for_managing,
            server_id=self.pserver_id.odoo_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        IPLine = self.env['server.ip.line']
        values = self._prepare_server_ip_line_values()
        line = IPLine.search([('ip_id', '=', values['ip_id']), ('server_id', '=', values['server_id'])])
        if not line:
            line = self.env['server.ip.line'].create(values)
        elif not line.for_managing and self.for_managing:
            line.for_managing = self.for_managing
        return line
