from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    website_id = fields.Many2one('website')
