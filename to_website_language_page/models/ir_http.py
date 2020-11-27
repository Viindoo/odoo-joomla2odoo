import werkzeug
from odoo import models
from odoo import http
from odoo.http import request
from odoo.tools.misc import frozendict

class Http(models.AbstractModel):
    _inherit = 'ir.http'
    
    @classmethod
    def _serve_page(cls):
        ctx = http.request.env.context.copy()
        ctx.update(page_filter_by_language=True)
        http.request.env.context = frozendict(ctx)
        res = super(Http, cls)._serve_page()
        if not res:
            ctx.update(page_filter_by_language=False)
            http.request.env.context = frozendict(ctx)
            req_page = request.httprequest.path
            page_domain = [('url', '=', req_page)] + request.website.website_domain()
            page = request.env['website.page'].sudo().search(page_domain, order='website_id asc', limit=1)
            pages = page.other_language_page_ids.filtered(lambda p: p.language_id.code == request.env.context.get('lang', ''))
            if pages:
                return werkzeug.utils.redirect(pages[0].url, code=302)
        return res
            
            
            

