# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.http import request

class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    language_id = fields.Many2one('res.lang', string='Language')
    child_id = fields.One2many(context={'search_for_one2many_fields': True})
    
    def _update_domain(self, domain):
        if self.env.context.get('search_for_one2many_fields', False) and (request.is_frontend or self.env.context.get('js_menu'), False):
            language_code = self.env.context.get('lang')
            domain += [
                '|',
                ('language_id', '=', False),
                ('language_id.code', '=', language_code)
            ]
        return domain

    @api.model
    def search(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(WebsiteMenu, self).search(domain, *args, **kwargs)
    
    @api.model
    def get_tree(self, website_id, menu_id=None):
        ctx = self.env.context.copy()
        ctx.update({'js_menu': True})
        return super(WebsiteMenu, self.with_context(ctx)).get_tree(website_id, menu_id)
    

