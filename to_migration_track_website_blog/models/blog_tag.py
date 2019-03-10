from odoo import models


class BlogTag(models.Model):
    _name = 'blog.tag'
    _inherit = ['blog.tag', 'abstract.joomla.migration.track']
