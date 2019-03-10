from odoo import fields, models


class EasyBlogTag(models.TransientModel):
    _name = 'joomla.easyblog.tag'
    _description = 'EasyBlog Tag'
    _inherit = 'abstract.j.model'
    _joomla_table = 'easyblog_tag'

    name = fields.Char(joomla_column='title')
    odoo_blog_tag_id = fields.Many2one('blog.tag')
