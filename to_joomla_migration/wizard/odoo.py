# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'

    from_joomla = fields.Boolean()


class WebsitePage(models.Model):
    _inherit = 'website.page'

    from_joomla = fields.Boolean()


class BlogPost(models.Model):
    _inherit = 'blog.post'

    from_joomla = fields.Boolean()


class BlogTag(models.Model):
    _inherit = 'blog.tag'

    from_joomla = fields.Boolean()


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    from_joomla = fields.Boolean()
