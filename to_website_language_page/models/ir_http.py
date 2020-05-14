from odoo import models
from odoo import http
from odoo.tools.misc import frozendict

class Http(models.AbstractModel):
    _inherit = 'ir.http'
    
    @classmethod
    def _serve_page(cls):
        ctx = http.request.env.context.copy()
        ctx.update(page_filter_by_language=True)
        http.request.env.context = frozendict(ctx)
        return super(Http, cls)._serve_page()

