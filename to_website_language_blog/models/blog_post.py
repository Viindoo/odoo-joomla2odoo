from odoo import api, fields, models
from odoo.osv import expression

class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    language_id = fields.Many2one('res.lang', related='blog_id.language_id', store=True)

    def _update_domain(self, domain):
        if self.env.context.get('blog_filter_by_language', False):
            language_code = self.env.context.get('lang', '')
            lang_domain = [
                '|',
                ('language_id', '=', False),
                ('language_id.code', '=', language_code)
            ]
            domain = expression.AND([domain, lang_domain])
        return domain

    @api.model
    def search(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(BlogPost, self).search(domain, *args, **kwargs)

    @api.model
    def _read_group_raw(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(BlogPost, self)._read_group_raw(domain, *args, **kwargs)
