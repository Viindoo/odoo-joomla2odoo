# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class JoomlaModel(models.AbstractModel):
    """
    This is base model for models that map to corresponding joomla database
    tables for easier to play with.

    Model attributes:
        _joomla_table: name of the corresponding joomla database table.

    Field attributes:
        joomla_column: use this attribute if you want to map the field to a
            column in the corresponding joomla database table. Value should be
            name of the corresponding column or True if the field name is
            exactly the column name.
    """
    _name = 'joomla.model'
    _description = 'Joomla Model Base Class'
    _joomla_table = None

    migration_id = fields.Many2one('joomla.migration', required=True,
                                   ondelete='cascade')


class JoomlaUser(models.TransientModel):
    _name = 'joomla.user'
    _description = 'Joomla User'
    _inherit = 'joomla.model'
    _joomla_table = 'users'

    joomla_id = fields.Integer(joomla_column='id')
    name = fields.Char(joomla_column=True)
    username = fields.Char(joomla_column=True)
    email = fields.Char(joomla_column=True)
    block = fields.Boolean(joomla_column=True)
    odoo_user_id = fields.Many2one('res.users')


class JoomlaCategory(models.TransientModel):
    _name = 'joomla.category'
    _description = 'Joomla Category'
    _inherit = 'joomla.model'
    _joomla_table = 'categories'

    joomla_id = fields.Integer(joomla_column='id')
    name = fields.Char(joomla_column='title')
    path = fields.Char(joomla_column=True)
    extension = fields.Char(joomla_column=True)
    parent_joomla_id = fields.Integer(joomla_column='parent_id')
    parent_id = fields.Many2one('joomla.category')


class JoomlaArticle(models.TransientModel):
    _name = 'joomla.article'
    _description = 'Joomla Article'
    _inherit = 'joomla.model'
    _joomla_table = 'content'

    joomla_id = fields.Integer(joomla_column='id')
    name = fields.Char(joomla_column='title')
    alias = fields.Char(joomla_column=True)
    author_joomla_id = fields.Integer(joomla_column='created_by')
    author_id = fields.Many2one('joomla.user')
    introtext = fields.Text(joomla_column=True)
    fulltext = fields.Text(joomla_column=True)
    images = fields.Text(joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    publish_up = fields.Datetime(joomla_column=True)
    state = fields.Integer(joomla_column=True)
    category_joomla_id = fields.Integer(joomla_column='catid')
    category_id = fields.Many2one('joomla.category')
    category_ids = fields.Many2many('joomla.category',
                                    compute='_compute_categories')
    language = fields.Char(joomla_column=True)
    metakey = fields.Text(joomla_column=True)
    metadesc = fields.Text(joomla_column=True)

    def _compute_categories(self):
        for article in self:
            categories = self.env['joomla.category']
            cat = article.category_id
            while cat:
                categories += cat
                cat = cat.parent_id
            article.category_ids = categories


class EasyBlogPost(models.TransientModel):
    _name = 'joomla.easyblog.post'
    _description = 'EasyBlog Post'
    _inherit = 'joomla.model'
    _joomla_table = 'easyblog_post'

    joomla_id = fields.Integer(joomla_column='id')
    name = fields.Char(joomla_column='title')
    permalink = fields.Char(joomla_column=True)
    author_joomla_id = fields.Integer(joomla_column='created_by')
    author_id = fields.Many2one('joomla.user')
    intro = fields.Text(joomla_column=True)
    content = fields.Text(joomla_column=True)
    image = fields.Text(joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    published = fields.Integer(joomla_column=True)
    publish_up = fields.Datetime(joomla_column=True)
    state = fields.Integer(joomla_column=True)
    language = fields.Char(joomla_column=True)
    meta_ids = fields.One2many('joomla.easyblog.meta', 'content_id')


class EasyBlogMeta(models.TransientModel):
    _name = 'joomla.easyblog.meta'
    _description = 'EasyBlog Meta'
    _inherit = 'joomla.model'
    _joomla_table = 'easyblog_meta'

    joomla_id = fields.Integer(joomla_column='id')
    type = fields.Char(joomla_column=True)
    content_joomla_id = fields.Integer(joomla_column='content_id')
    content_id = fields.Many2one('joomla.easyblog.post')
    keywords = fields.Text(joomla_column=True)
    description = fields.Text(joomla_column=True)
