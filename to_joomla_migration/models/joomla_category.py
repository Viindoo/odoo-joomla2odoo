from odoo import fields, models, api


class JoomlaCategory(models.TransientModel):
    _name = 'joomla.category'
    _description = 'Joomla Category'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'categories'

    name = fields.Char(joomla_column='title')
    alias = fields.Char(joomla_column=True)
    path = fields.Char(joomla_column=True)
    language = fields.Char(joomla_column=True)
    parent_id = fields.Many2one('joomla.category', joomla_column=True)
    menu_ids = fields.One2many('joomla.menu', 'category_id')
    extension = fields.Char(joomla_column=True)
    article_ids = fields.One2many('joomla.article', 'category_id')
