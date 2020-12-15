from odoo import  models, fields, api
from odoo.osv import expression


class Blog(models.Model):
    _inherit = 'blog.blog'
    
    def _get_current_language(self):
        language_code = self.env.context.get('lang', '')
        language = self.env['res.lang'].search([('code', '=', language_code)], limit=1)
        return language.id

    language_id = fields.Many2one('res.lang', default=_get_current_language)
    
    def _update_domain(self, domain):
        if self.env.context.get('blog_filter_by_language', False):
            language_code = self.env.context.get('lang', '')
            lang_domain = [
                '|', '|',
                ('language_id', '=', False),
                ('language_id.code', '=', language_code),
                ('language_id.url_code', '=', language_code)
            ]
            domain = expression.AND([domain, lang_domain])
        return domain

    @api.model
    def search(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(Blog, self).search(domain, *args, **kwargs)
    
    def all_tags(self, join=False, min_limit=1):
        tag_by_blog = super(Blog, self).all_tags(join, min_limit)
        if self.env.context.get('blog_filter_by_language', False):
            language_code = self.env.context.get('lang', '')
            if join:
                return tag_by_blog._filter_tags(language_code)
            for key, tags in tag_by_blog.items():
                tags = tags._filter_tags(language_code)
        return tag_by_blog

