from odoo import models


class ServerDns(models.Model):
    _inherit = 'server.dns'

    def _validate_name(self):
        if (self._context.get('joomla_migration')):
            return
        super(ServerDns, self)._validate_name()
