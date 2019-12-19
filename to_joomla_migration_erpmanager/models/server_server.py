from odoo import models, fields


class ServerServer(models.Model):
    _inherit = 'server.server'

    datacenter_id = fields.Many2one('server.dc', required=False)