# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    website_id = fields.Many2one('website')
