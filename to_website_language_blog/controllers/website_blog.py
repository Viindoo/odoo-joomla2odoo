import werkzeug
from odoo import http
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.tools.misc import frozendict
from odoo.addons.http_routing.models.ir_http import slug

def _enable_blog_filter_by_language():
    context = http.request.env.context.copy()
    context.update(blog_filter_by_language=True)
    http.request.env.context = frozendict(context)

class WebsiteBlogEx(WebsiteBlog):
    
    def _prepare_blog_values(self, blogs, blog=False, date_begin=False, date_end=False, tags=False, state=False, page=False):
        if not blogs:
            return werkzeug.utils.redirect('/', code=302)
        if blog and blog not in blogs:
            return werkzeug.utils.redirect('/blog/%s' % slug(blogs[0]), code=302)
        return super(WebsiteBlogEx, self)._prepare_blog_values(blogs, blog, date_begin, date_end, tags, state, page)
    
    @http.route()
    def blog(self, blog=None, tag=None, page=1, **opt):
        _enable_blog_filter_by_language()
        return super(WebsiteBlogEx, self).blog(blog, tag, page, **opt)
    
    @http.route()
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        _enable_blog_filter_by_language()
        return super(WebsiteBlogEx, self).blog_post(blog, blog_post, tag_id, page, enable_editor, **post)