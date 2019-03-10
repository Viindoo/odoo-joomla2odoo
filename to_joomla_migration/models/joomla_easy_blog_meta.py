from odoo import fields, models


class EasyBlogMeta(models.TransientModel):
    _name = 'joomla.easyblog.meta'
    _description = 'EasyBlog Meta'
    _inherit = 'abstract.j.model'
    _joomla_table = 'easyblog_meta'

    type = fields.Char(joomla_column=True)
    content_id = fields.Many2one('joomla.easyblog.post', joomla_column=True)
    keywords = fields.Text(joomla_column=True)
    description = fields.Text(joomla_column=True)

