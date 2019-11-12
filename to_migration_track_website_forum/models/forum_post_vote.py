from odoo import models


class ForumPostVote(models.Model):
    _name = 'forum.post.vote'
    _inherit = ['forum.post.vote', 'abstract.joomla.migration.track']
