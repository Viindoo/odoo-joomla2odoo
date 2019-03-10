from odoo import http
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.tools.misc import frozendict


def _enable_filter_by_language():
    context = http.request.env.context.copy()
    context.update(filter_by_language=True)
    http.request.env.context = frozendict(context)


class WebsiteBlogEx(WebsiteBlog):
    @http.route()
    def blog(self, blog=None, tag=None, page=1, **opt):
        _enable_filter_by_language()
        return super(WebsiteBlogEx, self).blog(blog, tag, page, **opt)
