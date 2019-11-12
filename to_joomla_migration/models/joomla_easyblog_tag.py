from odoo import models


class EasyBlogTag(models.TransientModel):
    _name = 'joomla.easyblog.tag'
    _description = 'EasyBlog Tag'
    _inherit = 'joomla.tag'
    _joomla_table = 'easyblog_tag'
