from odoo import fields, models, api
from odoo.osv import expression

class WebsitePage(models.Model):
    _inherit = 'website.page'
    
    language_id = fields.Many2one('res.lang', string='Language')
    other_language_page_ids = fields.Many2many('website.page', 'website_page_website_page_rel', 'source_page_id', 
           'des_page_id', string='Other Language Pages')
    
    def _update_domain(self, domain):
        if self.env.context.get('page_filter_by_language', False):
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
        return super(WebsitePage, self).search(domain, *args, **kwargs)

