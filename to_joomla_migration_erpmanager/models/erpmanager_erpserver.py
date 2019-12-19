import json

from odoo import models, fields


class ERPManagerERPServer(models.TransientModel):
    _name = 'erpmanager.erpserver'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager ERP Server'
    _joomla_table = 'erpmanager_erpserver'

    name = fields.Char(joomla_column='title')
    pserver_id = fields.Many2one('erpmanager.pserver', joomla_column=True)
    erpversion_id = fields.Many2one('erpmanager.erpversion', joomla_column=True)
    erpusername = fields.Char(joomla_column=True)
    erpusergroup = fields.Char(joomla_column=True)
    erpuserhomedir = fields.Char(joomla_column=True)
    erpsourcecode_loc = fields.Char(joomla_column=True)
    erpaddons_loc = fields.Text(joomla_column=True)
    working_ip_id = fields.Many2one('erpmanager.ip', joomla_column=True)
    odoo_id = fields.Many2one('server.odoo')

    def _get_addons_paths(self):
        self.ensure_one()
        return json.loads(self.erpaddons_loc).values()

    def _prepare_std_addons_path_values(self):
        self.ensure_one()
        paths = self._get_addons_paths()
        values = []
        for path in paths:
            server_path = self.env['server.dir.path'].create(dict(name=path))
            values.append((0, 0, dict(addons_path_id=server_path.id)))
        return values

    def _prepare_server_odoo_values(self):
        self.ensure_one()
        addons_path_values = self._prepare_std_addons_path_values()
        values = dict(
            name=self.name,
            pserver_id=self.pserver_id.odoo_id.id,
            odoo_version_id=self.erpversion_id.odoo_id.id,
            odoo_username=self.erpusername,
            odoo_usergroup=self.erpusergroup,
            odoo_user_base_dir=self.erpuserhomedir,
            odoo_sourcecode_loc=self.erpsourcecode_loc,
            std_addons_path_ids=addons_path_values
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_server_odoo_values()
        server = self.env['server.odoo'].create(values)
        return server
