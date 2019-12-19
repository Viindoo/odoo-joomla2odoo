from odoo import models, fields


class ERPManagerPServer(models.TransientModel):
    _name = 'erpmanager.pserver'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager PServer'
    _joomla_table = 'erpmanager_pserver'

    name = fields.Char(joomla_column='title')
    sshport = fields.Integer(joomla_column=True)
    os_id = fields.Many2one('erpmanager.os', joomla_column=True)
    odoo_id = fields.Many2one('server.server')

    def _prepare_server_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            ssh_port=self.sshport,
            os_id=self.os_id.odoo_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_server_values()
        server = self.env['server.server'].create(values)
        return server
