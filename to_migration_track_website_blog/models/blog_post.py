from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify


class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['blog.post', 'abstract.joomla.migration.track']

    sef_url = fields.Char(compute='_compute_sef_url', store=True)

    @api.depends('language_id', 'language_id.code', 'name',
                 'blog_id', 'blog_id.name')
    def _compute_sef_url(self):
        for post in self:
            url = ''
            post_ = post
            if post.language_id:
                post_ = post.with_context(lang=post.language_id.code)
                url = '/' + post_.language_id.code
            url += '/blog/{}-{}/post/{}-{}'.format(
                slugify(post_.blog_id.name), post_.blog_id.id,
                slugify(post_.name), post_.id)
            post.sef_url = url

