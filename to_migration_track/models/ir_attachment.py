from odoo import models


class Attachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'abstract.joomla.migration.track']
