# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slugify


class JoomlaMigrationTrack(models.AbstractModel):
    _name = 'joomla.migration.track'

    created_by_migration = fields.Boolean()
    old_website = fields.Char()
    old_website_model = fields.Char()
    old_website_record_id = fields.Integer()


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'joomla.migration.track']


class WebsitePage(models.Model):
    _name = 'website.page'
    _inherit = ['website.page', 'joomla.migration.track']

    def get_url(self):
        self.ensure_one()
        if self.language_id:
            return '/' + self.language_id.code + self.url
        return self.url


class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['blog.post', 'joomla.migration.track']

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
    _name = 'blog.tag'
    _inherit = ['blog.tag', 'joomla.migration.track']


class Attachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'joomla.migration.track']


class WebsiteRedirect(models.Model):
    _name = 'website.redirect'
    _inherit = ['website.redirect', 'joomla.migration.track']
