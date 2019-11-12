from odoo import models, fields


class EasyDiscussCategory(models.TransientModel):
    _name = 'joomla.easydiscuss.category'
    _inherit = 'abstract.joomla.model'
    _description = 'EasyDiscuss Category'
    _joomla_table = 'discuss_category'

    language = fields.Char(joomla_column=True)
