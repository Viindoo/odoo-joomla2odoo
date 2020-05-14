# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ForumForum(models.Model):
    _inherit = 'forum.forum'

    language_id = fields.Many2one('res.lang', string='Language')
    
    def _update_domain(self, domain):
        if self.env.context.get('forum_filter_by_language'):
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
        return super(ForumForum, self).search(domain, *args, **kwargs)
    

