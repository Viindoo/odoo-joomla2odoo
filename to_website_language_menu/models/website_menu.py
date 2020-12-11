from odoo import fields, models, api
from odoo.http import request
from odoo.osv import expression

class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    language_id = fields.Many2one('res.lang', string='Language')
    
    def _update_domain(self, domain):
        is_frontend = hasattr(request, 'is_frontend') and request.is_frontend or False
        if self.env.context.get('search_from_website', False) and (is_frontend or self.env.context.get('js_menu', False)):
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
        return super(WebsiteMenu, self).search(domain, *args, **kwargs)
    
    @api.model
    def get_tree(self, website_id, menu_id=None):
        ctx = self.env.context.copy()
        ctx.update({'js_menu': True})
        return super(WebsiteMenu, self.with_context(ctx)).get_tree(website_id, menu_id)
    

