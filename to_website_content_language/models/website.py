# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


def _get_current_language(self):
    language_code = self.env.context.get('lang')
    language = self.env['res.lang'].search([('code', '=', language_code)], limit=1)
    return language.id


class WebsitePage(models.Model):
    _inherit = 'website.page'

    language_id = fields.Many2one('res.lang', default=_get_current_language)
