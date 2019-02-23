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

    sef_url = fields.Char(compute='_compute_sef_url', store=True)

    @api.depends('url', 'language_id', 'language_id.code')
    def _compute_sef_url(self):
        for page in self:
            if page.language_id:
                page.sef_url = '/' + page.language_id.code + page.url
            else:
                page.sef_url = page.url


class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['blog.post', 'joomla.migration.track']

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


class BlogTag(models.Model):
    _name = 'blog.tag'
    _inherit = ['blog.tag', 'joomla.migration.track']


class Attachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'joomla.migration.track']


class WebsiteRedirect(models.Model):
    _name = 'website.redirect'
    _inherit = ['website.redirect', 'joomla.migration.track']
