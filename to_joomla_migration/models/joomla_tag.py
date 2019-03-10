from odoo import fields, models


class JoomlaTag(models.TransientModel):
    _name = 'joomla.tag'
    _description = 'Joomla Tag'
    _inherit = 'abstract.j.model'
    _joomla_table = 'tags'

    name = fields.Char(joomla_column='title')
    odoo_blog_tag_id = fields.Many2one('blog.tag')
