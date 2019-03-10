# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


def _get_current_language(self):
    language_code = self.env.context.get('lang')
    language = self.env['res.lang'].search([('code', '=', language_code)], limit=1)
    return language.id


class BlogPost(models.Model):
    _inherit = 'blog.post'

    language_id = fields.Many2one('res.lang', default=_get_current_language)

    def _update_domain(self, domain):
        if not self.env.context.get('filter_by_language'):
            return domain
        language_code = self.env.context.get('lang')
        return domain + [
            '|',
            ('language_id', '=', False),
            ('language_id.code', '=', language_code)
        ]

    @api.model
    def search(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(BlogPost, self).search(domain, *args, **kwargs)

    @api.model
    def _read_group_raw(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(BlogPost, self)._read_group_raw(domain, *args, **kwargs)
