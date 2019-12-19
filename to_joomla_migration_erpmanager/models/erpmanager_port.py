from odoo import models, fields


class ERPManagerPort(models.TransientModel):
    _name = 'erpmanager.port'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Port'
    _joomla_table = 'erpmanager_port'

    name = fields.Integer(joomla_column='number')
    pserver_id = fields.Many2one('erpmanager.pserver', joomla_column=True)
    reserved = fields.Boolean(joomla_column=True)
    oebackend_id = fields.Many2one('erpmanager.oebackend', joomla_column=True)
    odoo_id = fields.Many2one('server.port')

    def _prepare_server_port_values(self):
        self.ensure_one()
        values = dict(
            name=self.name,
            server_id=self.pserver_id.odoo_id.id,
            odoo_instance_id=self.oebackend_id.instance_id.odoo_id.id,
            reserved=self.reserved
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_server_port_values()
        port = self.env['server.port'].create(values)
        return port
