from odoo import http
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.tools.misc import frozendict

class WebsiteBlogEx(WebsiteBlog):
    @http.route()
    def blog(self, blog=None, tag=None, page=1, **opt):
        ctx = http.request.env.context.copy()
        ctx.update(blog_filter_by_language=True)
        http.request.env.context = frozendict(ctx)
        return super(WebsiteBlogEx, self).blog(blog, tag, page, **opt)
    
    @http.route()
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        if blog_post.language_id:
            if blog_post.language_id.code != http.request.env.context.get('lang'):
                raise http.request.not_found()
        return super(WebsiteBlogEx, self).blog_post(blog, blog_post, tag_id, page, enable_editor, **post)