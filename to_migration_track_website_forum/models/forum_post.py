from odoo import models


class ForumPost(models.Model):
    _name = 'forum.post'
    _inherit = ['forum.post', 'abstract.joomla.migration.track']
