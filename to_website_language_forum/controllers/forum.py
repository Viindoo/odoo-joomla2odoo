from odoo import http
from odoo.addons.website_forum.controllers.main import WebsiteForum
from odoo.tools.misc import frozendict

def _enable_forum_filter_by_language():
    context = http.request.env.context.copy()
    context.update(forum_filter_by_language=True)
    http.request.env.context = frozendict(context)


class WebsiteForumEx(WebsiteForum):
    @http.route()
    def forum(self, **kwargs):
        _enable_forum_filter_by_language()
        return super(WebsiteForumEx, self).forum(**kwargs)
    
    @http.route()
    def questions(self, forum, tag=None, page=1, filters='all', my=None, sorting=None, search='', **post):
        if forum.language_id:
            if forum.language_id.code != http.request.env.context.get('lang'):
                forum = http.request.env['forum.forum'].with_context(forum_filter_by_language=False).search([('language_id.code', '=', http.request.env.context.get('lang'))], limit=1)
                if not forum:
                    raise http.request.not_found()
        _enable_forum_filter_by_language()
        return super(WebsiteForumEx, self).questions(forum, tag, page, filters, my, sorting, search, **post)
    
    @http.route()
    def question(self, forum, question, **post):
        if question.language_id:
            if question.language_id.code != http.request.env.context.get('lang'):
                forum = http.request.env['forum.forum'].with_context(forum_filter_by_language=False).search([('language_id.code', '=', http.request.env.context.get('lang'))], limit=1)
                if not forum:
                    raise http.request.not_found()
                else:
                    return self.questions(forum, **post)
        _enable_forum_filter_by_language()
        return super(WebsiteForumEx, self).question(forum, question, **post)