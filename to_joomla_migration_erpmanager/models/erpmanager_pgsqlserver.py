import json

from odoo import models, fields


class ERPManagerPostgreSQLServer(models.TransientModel):
    _name = 'erpmanager.pgsqlserver'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager PostgreSQL Server'
    _joomla_table = 'erpmanager_pgsqlserver'

    name = fields.Char(joomla_column='title')
    pserver_id = fields.Many2one('erpmanager.pserver', joomla_column=True)
    postgresql_su = fields.Char(joomla_column=True)
    postgresql_passwd = fields.Char(joomla_column=True)
    postgresql_port = fields.Integer(joomla_column=True)
    default_template = fields.Char(joomla_column=True)
    functions_to_drop = fields.Text(joomla_column=True)
    odoo_id = fields.Many2one('server.postgresql')

    def _prepare_server_postgresql_values(self):
        self.ensure_one()
        functions_dict = json.loads(self.functions_to_drop)
        functions = '\n'.join(functions_dict.values())
        values = dict(
            name=self.name,
            pserver_id=self.pserver_id.odoo_id.id,
            username=self.postgresql_su,
            password=self.postgresql_passwd,
            port=self.postgresql_port,
            default_template=self.default_template,
            functions_to_drop=functions
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_server_postgresql_values()
        server = self.env['server.postgresql'].create(values)
        return server
