# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Page(models.Model):
    _inherit = 'website.page'

    website_id = fields.Many2one(related='view_id.website_id', store=True)
