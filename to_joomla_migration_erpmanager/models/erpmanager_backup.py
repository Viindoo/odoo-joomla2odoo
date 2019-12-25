from odoo import models, fields


class ERPManagerBackup(models.TransientModel):
    _name = 'erpmanager.backup'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Backup'
    _joomla_table = 'erpmanager_backup'

    instance_id = fields.Many2one('erpmanager.instance', joomla_column=True)
    backup_path = fields.Char(joomla_column=True)
    erpversion_id = fields.Many2one('erpmanager.erpversion', joomla_column=True)
    odoo_id = fields.Many2one('odoo.backup')

    def _prepare_backup_values(self):
        self.ensure_one()
        values = dict(
            name=self.backup_path,
            odoo_version_id=self.erpversion_id.odoo_id.id,
            instanceperm_id=self.instance_id.odoo_id.instanceperm_id.id,
            backup_server_id=self._context.get('backup_server').id
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_backup_values()
        if not values.get('instanceperm_id'):
            return False
        backup = self.env['odoo.backup'].create(values)
        return backup

    def migrate(self):
        backup_server = self.env['server.backup'].search([], limit=1)
        pserver = self.env['server.server'].search([], limit=1)
        if not backup_server:
            backup_server = self.env['server.backup'].create(dict(
                pserver_id=pserver.id,
                backup_path='/backups'
            ))
        backups = self.filtered(lambda b: b.instance_id).with_context(backup_server=backup_server)
        super(ERPManagerBackup, backups).migrate()
