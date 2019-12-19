from odoo import models


class ServerPostgreSQL(models.Model):
    _name = 'server.postgresql'
    _inherit = ['server.postgresql', 'abstract.joomla.migration.track']
