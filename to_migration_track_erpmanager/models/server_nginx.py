from odoo import models


class ServerNginx(models.Model):
    _name = 'server.nginx'
    _inherit = ['server.nginx', 'abstract.joomla.migration.track']
