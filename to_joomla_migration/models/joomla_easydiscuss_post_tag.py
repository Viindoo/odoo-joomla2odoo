from odoo import models, fields


class EasyDiscussPostTag(models.TransientModel):
    _name = 'joomla.easydiscuss.post.tag'
    _description = 'EasyDiscuss Post Tag'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'discuss_posts_tags'

    joomla_id = False
    post_id = fields.Many2one('joomla.easydiscuss.post', joomla_column=True)
    tag_id = fields.Many2one('joomla.easydiscuss.tag', joomla_column=True)
