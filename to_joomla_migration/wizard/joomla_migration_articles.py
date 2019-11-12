import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_article = fields.Boolean(default=True)
    category_ids = fields.One2many('joomla.category', 'migration_id')
    article_ids = fields.One2many('joomla.article', 'migration_id')
    article_map_ids = fields.One2many('joomla.migration.article.map', 'migration_id')

    def get_joomla_models(self):
        jmodels = super(JoomlaMigration, self).get_joomla_models()
        if self.include_article:
            for model in ['joomla.category', 'joomla.article', 'joomla.tag', 'joomla.article.tag', 'joomla.menu']:
                jmodels[model] = 200
        return jmodels

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_article:
            self._migrate_articles()

    def _migrate_articles(self):
        articles = self.article_ids
        page_articles = blog_articles = self.env['joomla.article']

        for m in self.article_map_ids:
            records = articles.filtered(lambda r: m.category_id in r.category_ids)
            if m.migrate_to == 'page':
                page_articles |= records
            elif m.migrate_to == 'blog':
                blog_articles |= records
            articles -= records

        page_articles.migrate_to_website_page()
        blog_articles.mapped('tag_ids').migrate_to_blog_tag()
        blog_articles.migrate_to_blog_post()

    def _get_records_to_reset(self):
        res = super(JoomlaMigration, self)._get_records_to_reset()
        pages = self.env['website.page'].get_migrated_data()
        views = pages.mapped('view_id')
        posts = self.env['blog.post'].get_migrated_data()
        tags = self.env['blog.tag'].get_migrated_data()
        res.extend([(pages, 500), (views, 525), (posts, 550), (tags, 575)])
        return res


class ArticleMap(models.TransientModel):
    _name = 'joomla.migration.article.map'
    _description = 'Article Migration Map'

    migration_id = fields.Many2one('joomla.migration', ondelete='cascade')
    category_id = fields.Many2one('joomla.category', required=True, ondelete='cascade')
    migrate_to = fields.Selection([('page', 'Page'), ('blog', 'Blog')], required=True, default='page')
