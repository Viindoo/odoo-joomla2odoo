from odoo import models


class ForumTag(models.Model):
    _name = 'forum.tag'
    _inherit = ['forum.tag', 'abstract.joomla.migration.track']
