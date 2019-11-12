from odoo import models


class MailMessage(models.Model):
    _name = 'mail.message'
    _inherit = ['mail.message', 'abstract.joomla.migration.track']
