# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slugify


class Partner(models.Model):
    _inherit = 'res.partner'

    from_joomla = fields.Boolean()


class WebsitePage(models.Model):
    _inherit = 'website.page'

    from_joomla = fields.Boolean()

    def get_url(self):
        self.ensure_one()
        if self.language_id:
            return '/' + self.language_id.code + self.url
        return self.url


class BlogPost(models.Model):
    _inherit = 'blog.post'

    from_joomla = fields.Boolean()

    def get_url(self):
        self.ensure_one()
        if self.language_id:
            self = self.with_context(lang=self.language_id.code)
            url = '/' + self.language_id.code
        else:
            url = ''
        url += '/blog/{}-{}/post/{}-{}'.format(
            slugify(self.blog_id.name), self.blog_id.id,
            slugify(self.name), self.id)
        return url


class BlogTag(models.Model):
    _inherit = 'blog.tag'

    from_joomla = fields.Boolean()


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    from_joomla = fields.Boolean()


class WebsiteRedirect(models.Model):
    _inherit = 'website.redirect'

    from_joomla = fields.Boolean()
