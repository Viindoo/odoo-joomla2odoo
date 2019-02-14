# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


def _get_current_language(self):
    language_code = self.env.context.get('lang')
    language = self.env['res.lang'].search([('code', '=', language_code)], limit=1)
    return language.id


class WebsitePage(models.Model):
    _inherit = 'website.page'

    language_id = fields.Many2one('res.lang', default=_get_current_language)


class Blog(models.Model):
    _inherit = 'blog.blog'

    def all_tags(self, min_limit=1):
        tag_by_blog = super(Blog, self).all_tags(min_limit)
        if self.env.context.get('filter_by_language'):
            language_code = self.env.context.get('lang')
            for blog_id in tag_by_blog:
                tags = tag_by_blog[blog_id]
                filtered_tags = tags.filtered(
                    lambda tag: tag.post_ids.filtered(
                        lambda post: (not post.language_id or
                                      post.language_id.code == language_code)
                    )
                )
                tag_by_blog[blog_id] = filtered_tags
        return tag_by_blog


class BlogPost(models.Model):
    _inherit = 'blog.post'

    language_id = fields.Many2one('res.lang', default=_get_current_language)

    def _update_domain(self, domain):
        if not self.env.context.get('filter_by_language'):
            return domain
        language_code = self.env.context.get('lang')
        return domain + [
            '|',
            ('language_id', '=', False),
            ('language_id.code', '=', language_code)
        ]

    @api.model
    def search(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(BlogPost, self).search(domain, *args, **kwargs)

    @api.model
    def _read_group_raw(self, domain, *args, **kwargs):
        domain = self._update_domain(domain)
        return super(BlogPost, self)._read_group_raw(domain, *args, **kwargs)
