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
    articles_count = fields.Integer(compute='_compute_articles_count')

    @api.depends('article_ids')
    def _compute_articles_count(self):
        for r in self:
            r.articles_count = len(r.article_ids)

    def name_get(self):
        result = []
        for r in self:
            if r.articles_count:
                result.append((r.id, '{} ({} Articles)'.format(r.name, r.articles_count)))
            else:
                result.append((r.id, r.name))
        return result
