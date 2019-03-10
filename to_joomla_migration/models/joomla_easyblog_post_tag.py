from odoo import fields, models


class EasyBlogPostTag(models.TransientModel):
    _name = 'joomla.easyblog.post.tag'
    _description = 'EasyBlog Post Tag'
    _inherit = 'abstract.j.model'
    _joomla_table = 'easyblog_post_tag'

    joomla_id = False
    tag_id = fields.Many2one('joomla.easyblog.tag', joomla_column=True)
    post_id = fields.Many2one('joomla.easyblog.post', joomla_column=True)
