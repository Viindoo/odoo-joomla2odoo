# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Blog(models.Model):
    _inherit = 'blog.blog'

    website_id = fields.Many2one('website')
