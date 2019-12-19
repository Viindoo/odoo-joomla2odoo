from odoo import models, fields


class ERPManagerProxyServer(models.TransientModel):
    _name = 'erpmanager.proxyserver'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Proxy Server'
    _joomla_table = 'erpmanager_proxyserver'

    name = fields.Char(joomla_column='title')
    pserver_id = fields.Many2one('erpmanager.pserver', joomla_column=True)
    sites_available = fields.Char(joomla_column=True)
    sites_enabled = fields.Char(joomla_column=True)
    ssl_dir = fields.Char(joomla_column=True)
    accesslog_folder = fields.Char(joomla_column=True)
    errlog_folder = fields.Char(joomla_column=True)
    pagespeedcache_folder = fields.Char(joomla_column=True)
    working_ip_id = fields.Many2one('erpmanager.ip', joomla_column=True)
    odoo_id = fields.Many2one('server.nginx')

    def _prepare_server_nginx_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            pserver_id=self.pserver_id.odoo_id.id,
            sites_available=self.sites_available,
            sites_enabled=self.sites_enabled,
            accesslog_folder=self.accesslog_folder,
            errlog_folder=self.errlog_folder,
            ssl_dir=self.ssl_dir,
            pagespeedcache_folder=self.pagespeedcache_folder
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_server_nginx_values()
        server = self.env['server.nginx'].create(values)
        return server
