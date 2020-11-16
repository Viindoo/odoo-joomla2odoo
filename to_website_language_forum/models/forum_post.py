from odoo import fields, models, api
from odoo.osv import expression


class ForumPost(models.Model):
    _inherit = 'forum.post'

    language_id = fields.Many2one('res.lang', related='forum_id.language_id', store=True, string='Language')
    
    def _update_domain(self, domain):
        if self.env.context.get('forum_filter_by_language', False):
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
        return super(ForumPost, self).search(domain, *args, **kwargs)
    

