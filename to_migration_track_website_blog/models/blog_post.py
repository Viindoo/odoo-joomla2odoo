from odoo import models


class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['blog.post', 'abstract.joomla.migration.track']
