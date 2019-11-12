from odoo import fields, models


class JoomlaArticleTag(models.TransientModel):
    _name = 'joomla.article.tag'
    _description = 'Joomla Article Tag'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'contentitem_tag_map'

    joomla_id = False
    article_id = fields.Many2one('joomla.article', joomla_column='content_item_id')
    tag_id = fields.Many2one('joomla.tag', joomla_column=True)
