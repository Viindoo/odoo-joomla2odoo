# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WebsitePage(models.Model):
    _inherit = 'website.page'

    language_id = fields.Many2one('res.lang')


class BlogPost(models.Model):
    _inherit = 'blog.post'

    language_id = fields.Many2one('res.lang')
