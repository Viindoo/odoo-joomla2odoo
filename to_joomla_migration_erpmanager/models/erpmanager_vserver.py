from odoo import models, fields


class ERPManagerVServer(models.TransientModel):
    _name = 'erpmanager.vserver'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Virtual Server'
    _joomla_table = 'erpmanager_vserver'

    name = fields.Char(joomla_column='title')
    ordering = fields.Integer(joomla_column=True)
    country_id = fields.Many2one('erpmanager.country', joomla_column=True)
    proxyserver_ids = fields.Many2many('erpmanager.proxyserver', joomla_relation='erpmanager_proxyserver_vserver_rel',
                                       joomla_column1='vserver_id', joomla_column2='proxyserver_id')
    pgsqlserver_ids = fields.Many2many('erpmanager.pgsqlserver', joomla_relation='erpmanager_pgsqlserver_vserver_rel',
                                       joomla_column1='vserver_id', joomla_column2='pgsqlserver_id')
    erpserver_ids = fields.Many2many('erpmanager.erpserver', joomla_relation='erpmanager_erpserver_vserver_rel',
                                     joomla_column1='vserver_id', joomla_column2='erpserver_id')
    odoo_id = fields.Many2one('odoo.vserver')

    def _prepare_odoo_vserver_values(self):
        self.ensure_one()
        proxyserver = self.proxyserver_ids[:1]
        pgsqlserver = self.pgsqlserver_ids[:1]
        erpserver = self.erpserver_ids[:1]
        values = dict(
            name=self.name,
            sequence=self.ordering,
            odoo_version_id=erpserver.erpversion_id.odoo_id.id,
            nginx_server_id=proxyserver.odoo_id.id,
            odoo_server_id=erpserver.odoo_id.id,
            pg_server_id=pgsqlserver.odoo_id.id,
            country_id=self.country_id.odoo_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_odoo_vserver_values()
        vserver = self.env['odoo.vserver'].create(values)
        return vserver
